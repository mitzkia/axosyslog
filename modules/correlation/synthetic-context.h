/*
 * Copyright (c) 2016 Balabit
 * Copyright (c) 2016 Balázs Scheidler
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
#ifndef CORRELATION_SYNTHETIC_CONTEXT_H_INCLUDED
#define CORRELATION_SYNTHETIC_CONTEXT_H_INCLUDED

#include "syslog-ng.h"
#include "correlation-key.h"
#include "template/templates.h"

typedef struct _SyntheticContext
{
  gint timeout;
  CorrelationScope scope;
  LogTemplate *id_template;
} SyntheticContext;

void synthetic_context_set_context_id_template(SyntheticContext *self, LogTemplate *context_id_template);
void synthetic_context_set_context_timeout(SyntheticContext *self, gint timeout);
void synthetic_context_set_context_scope(SyntheticContext *self, const gchar *scope, GError **error);

void synthetic_context_init(SyntheticContext *self);
void synthetic_context_deinit(SyntheticContext *self);

gint synthetic_context_lookup_context_scope(const gchar *context_scope);

#endif
