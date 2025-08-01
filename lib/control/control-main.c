/*
 * Copyright (c) 2002-2013 Balabit
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

#include "control-main.h"
#include "control-server-unix.h"
#include "control-commands.h"

ControlServer *
control_init(const gchar *control_name)
{
  ControlServer *control_server = control_server_unix_new(control_name);
  control_server_start(control_server);
  return control_server;
}

void
control_deinit(ControlServer *control_server)
{
  reset_control_command_list();
  if (control_server)
    {
      control_server_stop(control_server);
      control_server_free(control_server);
    }
}
