/*
 * Copyright (c) 2013 Balabit
 * Copyright (c) 2013 Balázs Scheidler
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

#ifndef AFSOCKET_OPTIONS_LIB_H_INCLUDED
#define AFSOCKET_OPTIONS_LIB_H_INCLUDED

#include <criterion/criterion.h>

#include "transport-mapper.h"

extern TransportMapper *transport_mapper;

static inline void
assert_transport_mapper_apply(TransportMapper *self, const gchar *transport)
{
  if (transport)
    transport_mapper_set_transport(self, transport);
  cr_assert(transport_mapper_apply_transport(self, configuration), "afsocket_apply_transport() failed");
}

static inline void
assert_transport_mapper_apply_fails(TransportMapper *self, const gchar *transport)
{
  if (transport)
    transport_mapper_set_transport(self, transport);
  cr_assert_not(transport_mapper_apply_transport(self, configuration),
                "afsocket_apply_transport() succeeded while we expected failure");
}

static inline void
assert_transport_mapper_transport(TransportMapper *options, const gchar *expected_transport)
{
  cr_assert_str_eq(options->transport, expected_transport, "TransportMapper contains a mismatching transport name");
}

static inline void
assert_transport_mapper_logproto(TransportMapper *options, const gchar *expected_logproto)
{
  cr_assert_str_eq(options->logproto, expected_logproto, "TransportMapper contains a mismatching log_proto name");
}

static inline void
assert_transport_mapper_stats_source(TransportMapper *options, gint stats_source)
{
  cr_assert_eq(options->stats_source, stats_source, "TransportMapper contains a mismatching stats_source");
}

static inline void
assert_transport_mapper_address_family(TransportMapper *options, gint address_family)
{
  cr_assert_eq(options->address_family, address_family, "TransportMapper address family mismatch");
}

static inline void
assert_transport_mapper_sock_type(TransportMapper *options, gint sock_type)
{
  cr_assert_eq(options->sock_type, sock_type, "TransportMapper sock_type mismatch");
}

static inline void
assert_transport_mapper_sock_proto(TransportMapper *options, gint sock_proto)
{
  cr_assert_eq(options->sock_proto, sock_proto, "TransportMapper sock_proto mismatch");
}

static inline void
assert_transport_mapper_transport_name(TransportMapper *options, const gchar *expected_transport_name)
{
  gsize len;
  const gchar *transport_name;

  transport_name = transport_mapper_get_transport_name(options, &len);
  cr_assert_str_eq(transport_name, expected_transport_name,
                   "TransportMapper transport_name mismatch %s <> %s",
                   transport_name, expected_transport_name);
}

#endif
