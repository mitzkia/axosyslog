/*
 * Copyright (c) 2015 Balabit
 * Copyright (c) 2015 Balazs Scheidler <balazs.scheidler@balabit.com>
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

#ifndef _SNG_PYTHON_LOGMSG_H
#define _SNG_PYTHON_LOGMSG_H

#include "python-module.h"

typedef struct _PyLogMessage
{
  PyObject_HEAD
  LogMessage *msg;
  PyObject *bookmark_data;
  gboolean cast_to_bytes;
} PyLogMessage;

extern PyTypeObject py_log_message_type;

int py_is_log_message(PyObject *obj);
PyObject *py_log_message_new(LogMessage *msg, GlobalConfig *cfg);

void py_log_message_global_init(void);


#endif
