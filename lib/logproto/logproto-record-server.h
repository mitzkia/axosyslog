/*
 * Copyright (c) 2002-2012 Balabit
 * Copyright (c) 1998-2012 Balázs Scheidler
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
#ifndef LOGPROTO_RECORD_SERVER_H_INCLUDED
#define LOGPROTO_RECORD_SERVER_H_INCLUDED

#include "logproto-server.h"

/*
 * LogProtoBinaryRecordServer
 *
 * This class reads input in equally sized chunks. The message is the
 * whole record, regardless of embedded NUL/NL characters.
 */
LogProtoServer *log_proto_binary_record_server_new(LogTransport *transport, const LogProtoServerOptions *options,
                                                   gint record_size);

/*
 * LogProtoPaddedRecordServer
 *
 * This class reads input in equally sized chunks. The message lasts
 * until the first EOL/NUL character within the chunk.
 */
LogProtoServer *log_proto_padded_record_server_new(LogTransport *transport, const LogProtoServerOptions *options,
                                                   gint record_size);


#endif
