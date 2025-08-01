/*
 * Copyright (c) 2018 One Identity
 * Copyright (c) 2013, 2014 Balabit
 * Copyright (c) 2013, 2014, 2015 Gergely Nagy
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

#ifndef SNG_RIEMANN_WORKER_H_INCLUDED
#define SNG_RIEMANN_WORKER_H_INCLUDED

#include "logthrdest/logthrdestdrv.h"

typedef struct
{
  LogThreadedDestWorker super;
  riemann_client_t *client;

  struct
  {
    riemann_event_t **list;
    gint n;
  } event;
} RiemannDestWorker;

LogThreadedDestWorker *riemann_dw_new(LogThreadedDestDriver *owner, gint worker_index);

#endif
