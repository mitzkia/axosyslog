/*
 * Copyright (c) 2017 Balabit
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

#include "python-module.h"
#include "compat-python.h"
#include "python-helpers.h"
#include "syslog-ng.h"
#include "reloc.h"

void
py_init_threads(void)
{
#if (PY_MAJOR_VERSION == 3 && PY_MINOR_VERSION < 7)
  PyEval_InitThreads();
#endif
}
