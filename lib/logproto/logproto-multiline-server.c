/*
 * Copyright (c) 2017 Balabit
 * Copyright (c) 2017 Balazs Scheidler <bazsi@balabit.hu>
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
#include "logproto/logproto-multiline-server.h"
#include "logproto/logproto-text-server.h"
#include "multi-line/multi-line-logic.h"

/*
 * This is basically a factory that takes multi-line related options and
 * constructs the appropriate LogProtoServer instance.
 */

LogProtoServer *
log_proto_multiline_server_new(LogTransport *transport,
                               const LogProtoServerOptions *options,
                               MultiLineLogic *multi_line)
{
  LogProtoServer *server = log_proto_text_server_new(transport, options);
  log_proto_text_server_set_multi_line(server, multi_line);
  return server;
}
