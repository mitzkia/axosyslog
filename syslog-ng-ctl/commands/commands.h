/*
 * Copyright (c) 2019 Balabit
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

#ifndef SYSLOG_NG_CTL_COMMANDS_H_INCLUDED
#define SYSLOG_NG_CTL_COMMANDS_H_INCLUDED 1

#include "syslog-ng.h"
#include "secret-storage/secret-storage.h"

#include <stdio.h>

extern GOptionEntry no_options[];

typedef struct _CommandDescriptor
{
  const gchar *mode;
  const GOptionEntry *options;
  const gchar *description;
  gint (*main)(gint argc, gchar *argv[], const gchar *mode, GOptionContext *ctx);
  struct _CommandDescriptor *subcommands;
} CommandDescriptor;

typedef gint (*CommandResponseHandlerFunc)(GString *response, gpointer user_data);

gint dispatch_command(const gchar *cmd);
gint attach_command(const gchar *cmd);
gint process_response_status(GString *response);
gboolean is_syslog_ng_running(void);

gint run(const gchar *control_name, gint argc, gchar **argv, CommandDescriptor *mode, GOptionContext *ctx);
#endif
