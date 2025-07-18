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

#ifndef APPHOOK_H_INCLUDED
#define APPHOOK_H_INCLUDED

#include "syslog-ng.h"

enum
{
  /* these states happen as a sequence and only happen once */
  AH_STARTUP,
  AH_POST_DAEMONIZED,
  AH_RUNNING,
  AH_PRE_SHUTDOWN,
  AH_SHUTDOWN,

  /* this item separates state-like hooks from events happening regularly in
   * the RUNNING state */
  __AH_STATE_MAX,

  /* these happen from time to time and don't update the current state of
   * the process */
  AH_CONFIG_PRE_PRE_INIT,  /* configuration pre_init() is to be called */
  AH_CONFIG_PRE_INIT,      /* configuration init() is to be called */
  AH_CONFIG_STOPPED,       /* configuration is deinitialized, threads have stopped */
  AH_CONFIG_CHANGED,       /* configuration changed, threads are running again */
  AH_REOPEN_FILES,         /* reopen files signal from syslog-ng-ctl */
};

typedef enum
{
  AHM_RUN_ONCE,
  AHM_RUN_REPEAT,
} ApplicationHookRunMode;

/* state-like hook entry points */
void app_startup(void);
void app_post_daemonized(void);
void app_running(void);
void app_pre_shutdown(void);
void app_shutdown(void);

/* stateless entry points */
void app_config_pre_pre_init(void);
void app_config_pre_init(void);
void app_config_stopped(void);
void app_config_changed(void);
void app_reopen_files(void);

typedef void (*ApplicationHookFunc)(gint type, gpointer user_data);
typedef void (*ApplicationThreadHookFunc)(gpointer user_data);

gboolean app_is_starting_up(void);
gboolean app_is_shutting_down(void);

void register_application_hook(gint type,
                               ApplicationHookFunc func, gpointer user_data,
                               ApplicationHookRunMode run_mode);

void register_application_thread_init_hook(ApplicationThreadHookFunc func, gpointer user_data);
void register_application_thread_deinit_hook(ApplicationThreadHookFunc func, gpointer user_data);

void app_thread_start(void);
void app_thread_stop(void);

#endif
