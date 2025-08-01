/*
 * Copyright (c) 2002-2013 Balabit
 * Copyright (c) 2021 Balazs Scheidler <bazsi77@gmail.com>
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

#ifndef CONTROL_COMMAND_THREAD_H_INCLUDED
#define CONTROL_COMMAND_THREAD_H_INCLUDED

#include "control.h"

gboolean control_command_thread_relates_to_connection(ControlCommandThread *self, ControlConnection *cc);

void control_command_thread_run(ControlCommandThread *self);
void control_command_thread_cancel(ControlCommandThread *self);
const gchar *control_command_thread_get_command(ControlCommandThread *self);

ControlCommandThread *control_command_thread_new(ControlConnection *cc, GString *cmd,
                                                 ControlCommandFunc func, gpointer user_data);
ControlCommandThread *control_command_thread_ref(ControlCommandThread *self);
void control_command_thread_unref(ControlCommandThread *self);

#endif
