/*
 * Copyright (c) 2012-2019 Balabit
 * Copyright (c) 2012-2013 Balázs Scheidler
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

#include <criterion/criterion.h>
#include "libtest/mock-transport.h"
#include "libtest/proto_lib.h"
#include "libtest/msg_parse_lib.h"

#include "logproto/logproto-record-server.h"


Test(log_proto, test_log_proto_binary_record_server_no_encoding)
{
  LogProtoServer *proto;

  proto = log_proto_binary_record_server_new(
            log_transport_mock_records_new(
              "0123456789ABCDEF0123456789ABCDEF", -1,
              "01234567\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n", -1,
              "01234567\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0", 32,
              /* utf8 */
              "árvíztűrőtükörfúrógép\n\n", 32,
              /* iso-8859-2 */
              "\xe1\x72\x76\xed\x7a\x74\xfb\x72\xf5\x74\xfc\x6b\xf6\x72\x66\xfa"      /*  |árvíztűrőtükörfú| */
              "\x72\xf3\x67\xe9\x70\n\n\n\n\n\n\n\n\n\n\n", -1,                       /*  |rógép|            */
              /* ucs4 */
              "\x00\x00\x00\xe1\x00\x00\x00\x72\x00\x00\x00\x76\x00\x00\x00\xed"      /* |...á...r...v...í| */
              "\x00\x00\x00\x7a\x00\x00\x00\x74\x00\x00\x01\x71\x00\x00\x00\x72", 32, /* |...z...t...ű...r|  */

              "01234", 5,
              LTM_EOF),
            get_inited_proto_server_options(), 32);
  assert_proto_server_fetch(proto, "0123456789ABCDEF0123456789ABCDEF", -1);
  assert_proto_server_fetch(proto, "01234567\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n", -1);
  assert_proto_server_fetch(proto, "01234567\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0", 32);
  assert_proto_server_fetch(proto, "árvíztűrőtükörfúrógép\n\n", -1);
  assert_proto_server_fetch(proto,
                            "\xe1\x72\x76\xed\x7a\x74\xfb\x72\xf5\x74\xfc\x6b\xf6\x72\x66\xfa"        /*  |.rv.zt.r.t.k.rf.| */
                            "\x72\xf3\x67\xe9\x70\n\n\n\n\n\n\n\n\n\n\n", -1);                        /*  |r.g.p|            */
  assert_proto_server_fetch(proto,
                            "\x00\x00\x00\xe1\x00\x00\x00\x72\x00\x00\x00\x76\x00\x00\x00\xed"        /* |...á...r...v...í| */
                            "\x00\x00\x00\x7a\x00\x00\x00\x74\x00\x00\x01\x71\x00\x00\x00\x72", 32);  /* |...z...t...q...r|  */
  assert_proto_server_fetch_failure(proto, LPS_ERROR, "Record size was set, and couldn't read enough bytes");
  log_proto_server_free(proto);
}

Test(log_proto, test_log_proto_padded_record_server_no_encoding)
{
  LogProtoServer *proto;

  proto = log_proto_padded_record_server_new(
            log_transport_mock_records_new(
              "0123456789ABCDEF0123456789ABCDEF", -1,
              "01234567\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n", -1,
              "01234567\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0", 32,
              /* utf8 */
              "árvíztűrőtükörfúrógép\n\n", 32,
              /* iso-8859-2 */
              "\xe1\x72\x76\xed\x7a\x74\xfb\x72\xf5\x74\xfc\x6b\xf6\x72\x66\xfa"      /*  |árvíztűrőtükörfú| */
              "\x72\xf3\x67\xe9\x70\n\n\n\n\n\n\n\n\n\n\n", -1,                       /*  |rógép|            */
              /* ucs4 */
              "\x00\x00\x00\xe1\x00\x00\x00\x72\x00\x00\x00\x76\x00\x00\x00\xed"      /* |...á...r...v...í| */
              "\x00\x00\x00\x7a\x00\x00\x00\x74\x00\x00\x01\x71\x00\x00\x00\x72", 32, /* |...z...t...ű...r|  */

              "01234", 5,
              LTM_EOF),
            get_inited_proto_server_options(), 32);
  assert_proto_server_fetch(proto, "0123456789ABCDEF0123456789ABCDEF", -1);
  assert_proto_server_fetch(proto, "01234567", -1);
  assert_proto_server_fetch(proto, "01234567", -1);

  /* no encoding: utf8 remains utf8 */
  assert_proto_server_fetch(proto, "árvíztűrőtükörfúrógép", -1);

  /* no encoding: iso-8859-2 remains iso-8859-2 */
  assert_proto_server_fetch(proto,
                            "\xe1\x72\x76\xed\x7a\x74\xfb\x72\xf5\x74\xfc\x6b\xf6\x72\x66\xfa" /*  |.rv.zt.r.t.k.rf.| */
                            "\x72\xf3\x67\xe9\x70",                                            /*  |r.g.p|            */
                            -1);
  /* no encoding, ucs4 becomes an empty string as it starts with a zero byte */
  assert_proto_server_fetch(proto, "", -1);
  assert_proto_server_fetch_failure(proto, LPS_ERROR, "Record size was set, and couldn't read enough bytes");
  log_proto_server_free(proto);
}


Test(log_proto, test_log_proto_padded_record_server_ucs4)
{
  LogProtoServer *proto;

  log_proto_server_options_set_encoding(&proto_server_options, "ucs-4");
  proto = log_proto_padded_record_server_new(
            log_transport_mock_records_new(
              /* ucs4, terminated by record size */
              "\x00\x00\x00\xe1\x00\x00\x00\x72\x00\x00\x00\x76\x00\x00\x00\xed"      /* |...á...r...v...í| */
              "\x00\x00\x00\x7a\x00\x00\x00\x74\x00\x00\x01\x71\x00\x00\x00\x72", 32, /* |...z...t...ű...r|  */

              /* ucs4, terminated by ucs4 encododed NL at the end */
              "\x00\x00\x00\xe1\x00\x00\x00\x72\x00\x00\x00\x76\x00\x00\x00\xed"      /* |...á...r...v...í| */
              "\x00\x00\x00\x7a\x00\x00\x00\x74\x00\x00\x01\x71\x00\x00\x00\n", 32,   /* |...z...t...ű|  */

              "01234", 5,
              LTM_EOF),
            get_inited_proto_server_options(), 32);
  assert_proto_server_fetch(proto, "árvíztűr", -1);
  assert_proto_server_fetch(proto, "árvíztű", -1);
  assert_proto_server_fetch_failure(proto, LPS_ERROR, "Record size was set, and couldn't read enough bytes");
  log_proto_server_free(proto);
}

Test(log_proto, test_log_proto_padded_record_server_invalid_ucs4)
{
  LogProtoServer *proto;

  log_proto_server_options_set_encoding(&proto_server_options, "ucs-4");
  proto = log_proto_padded_record_server_new(
            /* 31 bytes record size */
            log_transport_mock_records_new(
              /* invalid ucs4, trailing zeroes at the end */
              "\x00\x00\x00\xe1\x00\x00\x00\x72\x00\x00\x00\x76\x00\x00\x00\xed"      /* |...á...r...v...í| */
              "\x00\x00\x00\x7a\x00\x00\x00\x74\x00\x00\x01\x71\x00\x00\x00", 31, /* |...z...t...ű...r|  */
              LTM_EOF),
            get_inited_proto_server_options(), 31);
  assert_proto_server_fetch_failure(proto, LPS_ERROR,
                                    "Byte sequence too short, cannot convert an individual frame in its entirety");
  log_proto_server_free(proto);
}

Test(log_proto, test_log_proto_padded_record_server_iso_8859_2)
{
  LogProtoServer *proto;

  log_proto_server_options_set_encoding(&proto_server_options, "iso-8859-2");
  proto = log_proto_padded_record_server_new(
            /* 32 bytes record size */
            log_transport_mock_records_new(

              /* iso-8859-2, deliberately contains
               * accented chars so utf8 representation
               * becomes longer than the record size */
              "\xe1\x72\x76\xed\x7a\x74\xfb\x72\xf5\x74\xfc\x6b\xf6\x72\x66\xfa"       /*  |árvíztűrőtükörfú| */
              "\x72\xf3\x67\xe9\x70\xe9\xe9\xe9\xe9\xe9\xe9\xe9\xe9\xe9\xe9\xe9", -1,  /*  |rógépééééééééééé| */
              LTM_EOF),
            get_inited_proto_server_options(), 32);
  assert_proto_server_fetch(proto, "árvíztűrőtükörfúrógépééééééééééé", -1);
  assert_proto_server_fetch_failure(proto, LPS_EOF, NULL);
  log_proto_server_free(proto);
}
