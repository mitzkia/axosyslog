/*
 * Copyright (c) 2014 Balabit
 * Copyright (c) 2013 Tihamer Petrovics <tihameri@gmail.com>
 * Copyright (c) 2014 Gergely Nagy <algernon@balabit.hu>
 * Copyright (c) 2021 Szilárd Parrag
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

#ifndef REDIS_WORKER_H_INCLUDED
#define REDIS_WORKER_H_INCLUDED

#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wswitch-default"
#include <hiredis/hiredis.h>
#pragma GCC diagnostic pop

#include "syslog-ng.h"
#include "logthrdest/logthrdestdrv.h"


typedef struct _RedisDestWorker
{
  LogThreadedDestWorker super;
  redisContext *c;
  gint argc;
  gchar **argv;
  size_t *argvlen;

} RedisDestWorker;

LogThreadedDestWorker *redis_worker_new(LogThreadedDestDriver *owner, gint worker_index);

#endif
