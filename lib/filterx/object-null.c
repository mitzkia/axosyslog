/*
 * Copyright (c) 2023 Balazs Scheidler <balazs.scheidler@axoflow.com>
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
#include "object-null.h"
#include "filterx-globals.h"

static FilterXObject *null_object;

static gboolean
_truthy(FilterXObject *s)
{
  return FALSE;
}

static gboolean
_marshal(FilterXObject *s, GString *repr, LogMessageValueType *t)
{
  *t = LM_VT_NULL;
  return TRUE;
}

gboolean
null_format_json(GString *json)
{
  g_string_append_len(json, "null", 4);
  return TRUE;
}

gboolean
null_repr(GString *repr)
{
  return null_format_json(repr);
}

static gboolean
_format_json(FilterXObject *s, GString *json)
{
  return null_format_json(json);
}

static gboolean
_null_repr(FilterXObject *s, GString *repr)
{
  return null_repr(repr);
}

FilterXObject *
_null_wrap(void)
{
  return filterx_object_new(&FILTERX_TYPE_NAME(null));
}

FilterXObject *
filterx_null_new(void)
{
  return filterx_object_ref(null_object);
}

FILTERX_DEFINE_TYPE(null, FILTERX_TYPE_NAME(object),
                    .marshal = _marshal,
                    .format_json = _format_json,
                    .repr = _null_repr,
                    .truthy = _truthy,
                   );

void
filterx_null_global_init(void)
{
  null_object = _null_wrap();
  filterx_object_hibernate(null_object);
}

void
filterx_null_global_deinit(void)
{
  filterx_object_unhibernate_and_free(null_object);
}
