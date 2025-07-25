/*
 * Copyright (c) 2024 Attila Szakacs
 *
 * This program is free software: you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 *
 * As an additional exemption you are allowed to compile & link against the
 * OpenSSL libraries as published by the OpenSSL project. See the file
 * COPYING for details.
 *
 */

#include "object-otel-kvlist.hpp"
#include "otel-field-converter.hpp"

#include "compat/cpp-start.h"
#include "filterx/object-extractor.h"
#include "filterx/object-string.h"
#include "filterx/object-null.h"
#include "filterx/object-message-value.h"
#include "filterx/filterx-eval.h"
#include "compat/cpp-end.h"

#include <google/protobuf/reflection.h>
#include <google/protobuf/util/json_util.h>

#include <stdexcept>
#include <string.h>

/* The deprecated MutableRepeatedPtrField() does not have a proper alternative. */
#pragma GCC diagnostic ignored "-Wdeprecated-declarations"

using namespace syslogng::grpc::otel::filterx;
using opentelemetry::proto::common::v1::KeyValueList;
using opentelemetry::proto::common::v1::AnyValue;

/* C++ Implementations */

thread_local KeyValueList KVList::cached_value;

KVList::KVList(FilterXOtelKVList *s) :
  super(s),
  repeated_kv(new RepeatedPtrField<KeyValue>()),
  borrowed(false)
{
}

KVList::KVList(FilterXOtelKVList *s, RepeatedPtrField<KeyValue> *k) :
  super(s),
  repeated_kv(k),
  borrowed(true)
{
}

KVList::KVList(FilterXOtelKVList *s, FilterXObject *protobuf_object) :
  super(s),
  repeated_kv(new RepeatedPtrField<KeyValue>()),
  borrowed(false)
{
  const gchar *value;
  gsize length;
  if (!filterx_object_extract_protobuf_ref(protobuf_object, &value, &length))
    {
      delete repeated_kv;
      throw std::runtime_error("Argument is not a protobuf object");
    }

  KeyValueList temp_kvlist;
  if (!temp_kvlist.ParsePartialFromArray(value, length))
    {
      delete repeated_kv;
      throw std::runtime_error("Failed to parse from protobuf object");
    }

  repeated_kv->CopyFrom(*temp_kvlist.mutable_values());
}

KVList::KVList(const KVList &o, FilterXOtelKVList *s) :
  super(s),
  repeated_kv(new RepeatedPtrField<KeyValue>()),
  borrowed(false)
{
  repeated_kv->CopyFrom(*o.repeated_kv);
}

KVList::~KVList()
{
  if (!borrowed)
    delete repeated_kv;
}

std::string
KVList::marshal(void)
{
  KeyValueList temp_kvlist;
  temp_kvlist.mutable_values()->CopyFrom(*repeated_kv);
  return temp_kvlist.SerializePartialAsString();
}

KeyValue *
KVList::get_mutable_kv_for_key(const std::string &key) const
{
  for (int i = 0; i < repeated_kv->size(); i++)
    {
      KeyValue &possible_kv = repeated_kv->at(i);

      if (possible_kv.key().compare(key) == 0)
        return &possible_kv;
    }

  return nullptr;
}

bool
KVList::set_subscript(FilterXObject *key, FilterXObject **value)
{
  std::string key_str;
  try
    {
      key_str = extract_string_from_object(key);
    }
  catch (const std::runtime_error &)
    {
      filterx_eval_push_error_info_printf("Failed to set OTel KVList element", NULL,
                                          "Key must be string type, got: %s",
                                          filterx_object_get_type_name(key));
      return false;
    }

  ProtobufFieldConverter *converter = get_otel_protobuf_field_converter(FieldDescriptor::TYPE_MESSAGE);

  KeyValue *kv = get_mutable_kv_for_key(key_str);
  if (!kv)
    {
      kv = repeated_kv->Add();
      kv->set_key(key_str);
    }

  FilterXObject *assoc_object = NULL;
  if (!converter->set(kv, "value", *value, &assoc_object))
    return false;

  filterx_object_unref(*value);
  *value = assoc_object;
  return true;
}

FilterXObject *
KVList::get_subscript(FilterXObject *key)
{
  std::string key_str;
  try
    {
      key_str = extract_string_from_object(key);
    }
  catch (const std::runtime_error &)
    {
      filterx_eval_push_error_info_printf("Failed to get OTel KVList element", NULL,
                                          "Key must be string type, got: %s",
                                          filterx_object_get_type_name(key));
      return nullptr;
    }

  ProtobufFieldConverter *converter = get_otel_protobuf_field_converter(FieldDescriptor::TYPE_MESSAGE);
  KeyValue *kv = get_mutable_kv_for_key(key_str);
  if (!kv)
    return nullptr;

  return converter->get(kv, "value");
}

bool
KVList::is_key_set(FilterXObject *key) const
{
  try
    {
      return !!get_mutable_kv_for_key(extract_string_from_object(key));
    }
  catch (const std::runtime_error &)
    {
      filterx_eval_push_error_info_printf("Failed to check OTel KVList element", NULL,
                                          "Key must be string type, got: %s",
                                          filterx_object_get_type_name(key));
      return false;
    }
}

bool
KVList::unset_key(FilterXObject *key)
{
  std::string key_str;
  try
    {
      key_str = extract_string_from_object(key);
    }
  catch (const std::runtime_error &)
    {
      filterx_eval_push_error_info_printf("Failed to unset OTel KVList element", NULL,
                                          "Key must be string type, got: %s",
                                          filterx_object_get_type_name(key));
      return false;
    }

  for (int i = 0; i < repeated_kv->size(); i++)
    {
      KeyValue &possible_kv = repeated_kv->at(i);
      if (possible_kv.key().compare(key_str) == 0)
        {
          repeated_kv->DeleteSubrange(i, 1);
          return true;
        }
    }

  return true;
}

uint64_t
KVList::len() const
{
  return (uint64_t) repeated_kv->size();
}

bool
KVList::iter(FilterXDictIterFunc func, gpointer user_data) const
{
  ProtobufFieldConverter *converter = get_otel_protobuf_field_converter(FieldDescriptor::TYPE_MESSAGE);

  for (int i = 0; i < repeated_kv->size(); i++)
    {
      KeyValue &kv = repeated_kv->at(i);

      FILTERX_STRING_DECLARE_ON_STACK(key, kv.key().c_str(), kv.key().length());
      FilterXObject *value = converter->get(&kv, "value");

      bool result = func(key, value, user_data);

      filterx_object_unref(key);
      filterx_object_unref(value);
      if (!result)
        return false;
    }

  return true;
}

const RepeatedPtrField<KeyValue> &
KVList::get_value() const
{
  return *repeated_kv;
}

const google::protobuf::Message &
KVList::get_protobuf_value() const
{
  cached_value.mutable_values()->CopyFrom(*repeated_kv);
  return static_cast<const google::protobuf::Message &>(cached_value);
}

/* C Wrappers */

static void
_free(FilterXObject *s)
{
  FilterXOtelKVList *self = (FilterXOtelKVList *) s;

  delete self->cpp;
  self->cpp = NULL;

  filterx_object_free_method(s);
}

static gboolean
_set_subscript(FilterXDict *s, FilterXObject *key, FilterXObject **new_value)
{
  FilterXOtelKVList *self = (FilterXOtelKVList *) s;

  return self->cpp->set_subscript(key, new_value);
}

static FilterXObject *
_get_subscript(FilterXDict *s, FilterXObject *key)
{
  FilterXOtelKVList *self = (FilterXOtelKVList *) s;

  return self->cpp->get_subscript(key);
}

static gboolean
_is_key_set(FilterXDict *s, FilterXObject *key)
{
  FilterXOtelKVList *self = (FilterXOtelKVList *) s;

  return self->cpp->is_key_set(key);
}

static gboolean
_unset_key(FilterXDict *s, FilterXObject *key)
{
  FilterXOtelKVList *self = (FilterXOtelKVList *) s;

  return self->cpp->unset_key(key);
}

static guint64
_len(FilterXDict *s)
{
  FilterXOtelKVList *self = (FilterXOtelKVList *) s;

  return self->cpp->len();
}

static gboolean
_iter(FilterXDict *s, FilterXDictIterFunc func, gpointer user_data)
{
  FilterXOtelKVList *self = (FilterXOtelKVList *) s;

  return self->cpp->iter(func, user_data);
}

static gboolean
_truthy(FilterXObject *s)
{
  return TRUE;
}

static gboolean
_marshal(FilterXObject *s, GString *repr, LogMessageValueType *t)
{
  FilterXOtelKVList *self = (FilterXOtelKVList *) s;

  std::string serialized = self->cpp->marshal();

  g_string_truncate(repr, 0);
  g_string_append_len(repr, serialized.c_str(), serialized.length());
  *t = LM_VT_PROTOBUF;
  return TRUE;
}

static void
_init_instance(FilterXOtelKVList *self)
{
  filterx_dict_init_instance(&self->super, &FILTERX_TYPE_NAME(otel_kvlist));

  self->super.get_subscript = _get_subscript;
  self->super.set_subscript = _set_subscript;
  self->super.is_key_set = _is_key_set;
  self->super.unset_key = _unset_key;
  self->super.len = _len;
  self->super.iter = _iter;
}

FilterXObject *
_filterx_otel_kvlist_clone(FilterXObject *s)
{
  FilterXOtelKVList *self = (FilterXOtelKVList *) s;

  FilterXOtelKVList *clone = g_new0(FilterXOtelKVList, 1);
  _init_instance(clone);

  try
    {
      clone->cpp = new KVList(*self->cpp, clone);
    }
  catch (const std::runtime_error &)
    {
      g_assert_not_reached();
    }

  return &clone->super.super;
}

FilterXObject *
filterx_otel_kvlist_new_from_args(FilterXExpr *s, FilterXObject *args[], gsize args_len)
{
  FilterXOtelKVList *self = g_new0(FilterXOtelKVList, 1);
  _init_instance(self);

  try
    {
      if (!args || args_len == 0)
        {
          self->cpp = new KVList(self);
        }
      else if (args_len == 1)
        {
          FilterXObject *arg = args[0];
          FilterXObject *dict_arg = filterx_ref_unwrap_ro(arg);
          if (filterx_object_is_type(dict_arg, &FILTERX_TYPE_NAME(dict)))
            {
              self->cpp = new KVList(self);
              if (!filterx_dict_merge(&self->super.super, dict_arg))
                throw std::runtime_error("Failed to merge dict");
            }
          else
            {
              self->cpp = new KVList(self, arg);
            }
        }
      else
        {
          throw std::runtime_error("Invalid number of arguments");
        }
    }
  catch (const std::runtime_error &e)
    {
      filterx_eval_push_error_info_printf("Failed to create OTel KVList object", NULL, "%s", e.what());
      filterx_object_unref(&self->super.super);
      return NULL;
    }

  return &self->super.super;
}

static FilterXObject *
_new_borrowed(RepeatedPtrField<KeyValue> *kvlist)
{
  FilterXOtelKVList *self = g_new0(FilterXOtelKVList, 1);
  _init_instance(self);

  self->cpp = new KVList(self, kvlist);

  return &self->super.super;
}

FILTERX_SIMPLE_FUNCTION(otel_kvlist, filterx_otel_kvlist_new_from_args);

FilterXObject *
KVListFieldConverter::get(google::protobuf::Message *message, ProtoReflectors reflectors)
{
  if (reflectors.field_descriptor->is_repeated())
    {
      auto repeated_fields = reflectors.reflection->MutableRepeatedPtrField<KeyValue>(message, reflectors.field_descriptor);
      return _new_borrowed(repeated_fields);
    }

  try
    {
      Message *nestedMessage = reflectors.reflection->MutableMessage(message, reflectors.field_descriptor);
      KeyValueList *kvlist = dynamic_cast<KeyValueList *>(nestedMessage);
      return _new_borrowed(kvlist->mutable_values());
    }
  catch(const std::bad_cast &e)
    {
      g_assert_not_reached();
    }
}

static RepeatedPtrField<KeyValue> *
_get_repeated_kv(google::protobuf::Message *message, syslogng::grpc::ProtoReflectors reflectors)
{
  RepeatedPtrField<KeyValue> *repeated_kv;

  if (reflectors.field_descriptor->is_repeated())
    {
      try
        {
          repeated_kv = reflectors.reflection->MutableRepeatedPtrField<KeyValue>(message, reflectors.field_descriptor);
        }
      catch(const std::bad_cast &e)
        {
          g_assert_not_reached();
        }
    }
  else
    {
      KeyValueList *kvlist;
      try
        {
          kvlist = dynamic_cast<KeyValueList *>(reflectors.reflection->MutableMessage(message, reflectors.field_descriptor));
          repeated_kv = kvlist->mutable_values();
        }
      catch(const std::bad_cast &e)
        {
          g_assert_not_reached();
        }
    }

  return repeated_kv;
}

static gboolean
_add_elem_to_repeated_kv(FilterXObject *key_obj, FilterXObject *value_obj, gpointer user_data)
{
  RepeatedPtrField<KeyValue> *repeated_kv = (RepeatedPtrField<KeyValue> *) user_data;

  const gchar *key;
  gsize key_len;
  if (!filterx_object_extract_string_ref(key_obj, &key, &key_len))
    return false;

  KeyValue *kv = repeated_kv->Add();
  kv->set_key(key, key_len);

  FilterXObject *assoc_object = NULL;
  if (!syslogng::grpc::otel::any_value_field.direct_set(kv->mutable_value(), value_obj, &assoc_object))
    return false;

  filterx_object_unref(assoc_object);
  return true;
}

static bool
_set_kvlist_field_from_dict(google::protobuf::Message *message, syslogng::grpc::ProtoReflectors reflectors,
                            FilterXObject *object, FilterXObject **assoc_object)
{
  RepeatedPtrField<KeyValue> *repeated_kv = _get_repeated_kv(message, reflectors);
  if (!filterx_dict_iter(object, _add_elem_to_repeated_kv, repeated_kv))
    return false;

  *assoc_object = _new_borrowed(repeated_kv);
  return true;
}

bool
KVListFieldConverter::set(google::protobuf::Message *message, ProtoReflectors reflectors,
                          FilterXObject *object, FilterXObject **assoc_object)
{
  FilterXObject *object_unwrapped = filterx_ref_unwrap_rw(object);
  if (!filterx_object_is_type(object_unwrapped, &FILTERX_TYPE_NAME(otel_kvlist)))
    {
      if (filterx_object_is_type(object_unwrapped, &FILTERX_TYPE_NAME(dict)))
        return _set_kvlist_field_from_dict(message, reflectors, object_unwrapped, assoc_object);

      if (filterx_object_is_type(object_unwrapped, &FILTERX_TYPE_NAME(message_value)))
        {
          FilterXObject *unmarshalled = filterx_object_unmarshal(object_unwrapped);
          FilterXObject *unwrapped = filterx_ref_unwrap_ro(unmarshalled);
          bool success = filterx_object_is_type_or_ref(unwrapped, &FILTERX_TYPE_NAME(dict)) &&
                         _set_kvlist_field_from_dict(message, reflectors, unwrapped, assoc_object);
          filterx_object_unref(unmarshalled);
          return success;
        }

      filterx_eval_push_error_info_printf("Failed to convert field", NULL,
                                          "Type for field %s must be dict or otel_kvlist, got: %s",
                                          reflectors.field_type_name(),
                                          filterx_object_get_type_name(object));
      return false;
    }

  FilterXOtelKVList *filterx_kvlist = (FilterXOtelKVList *) object_unwrapped;

  RepeatedPtrField<KeyValue> *repeated_kv = _get_repeated_kv(message, reflectors);
  repeated_kv->CopyFrom(filterx_kvlist->cpp->get_value());

  KVList *new_kvlist;
  try
    {
      new_kvlist = new KVList(filterx_kvlist, repeated_kv);
    }
  catch (const std::runtime_error &)
    {
      g_assert_not_reached();
    }

  delete filterx_kvlist->cpp;
  filterx_kvlist->cpp = new_kvlist;

  return true;
}

bool
KVListFieldConverter::add(google::protobuf::Message *message, ProtoReflectors reflectors, FilterXObject *object)
{
  throw std::runtime_error("DatetimeFieldConverter: add operation is not supported");
}

KVListFieldConverter syslogng::grpc::otel::filterx::kvlist_field_converter;

static FilterXObject *
_list_factory(FilterXObject *self)
{
  return filterx_otel_array_new();
}

static FilterXObject *
_dict_factory(FilterXObject *self)
{
  return filterx_otel_kvlist_new();
}

static gboolean
_repr(FilterXObject *s, GString *repr)
{
  FilterXOtelKVList *self = (FilterXOtelKVList *) s;

  try
    {
      std::string cstring = self->cpp->repr();
      g_string_assign(repr, cstring.c_str());
    }
  catch (const std::runtime_error &e)
    {
      filterx_eval_push_error_info_printf("Failed to call repr() on OTel KVList object", NULL, "%s", e.what());
      return FALSE;
    }

  return TRUE;
}

FILTERX_DEFINE_TYPE(otel_kvlist, FILTERX_TYPE_NAME(dict),
                    .is_mutable = TRUE,
                    .marshal = _marshal,
                    .clone = _filterx_otel_kvlist_clone,
                    .truthy = _truthy,
                    .list_factory = _list_factory,
                    .dict_factory = _dict_factory,
                    .repr = _repr,
                    .free_fn = _free,
                   );
