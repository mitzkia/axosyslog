/*
 * Copyright (c) 2002-2013 Balabit
 * Copyright (c) 1998-2013 Balázs Scheidler
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

#ifndef CONTROL_CLIENT_H
#define CONTROL_CLIENT_H 1

#include "syslog-ng.h"
#include "commands/commands.h"

typedef struct _ControlClient ControlClient;

ControlClient *control_client_new(const gchar *path);
gboolean control_client_connect(ControlClient *self);
gint control_client_send_command(ControlClient *self, const gchar *cmd, gboolean attach);
gint control_client_read_reply(ControlClient *self, CommandResponseHandlerFunc cb, gpointer user_data);
void control_client_free(ControlClient *self);

#endif
