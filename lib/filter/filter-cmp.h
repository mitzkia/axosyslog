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

#ifndef FILTER_CMP_H_INCLUDED
#define FILTER_CMP_H_INCLUDED

#include "filter-expr.h"
#include "template/templates.h"

#define FCMP_EQ                   0x0001
#define FCMP_LT                   0x0002
#define FCMP_GT                   0x0004
#define FCMP_TYPE_AWARE           0x0010
#define FCMP_STRING_BASED         0x0020
#define FCMP_NUM_BASED            0x0040
#define FCMP_TYPE_AND_VALUE_BASED 0x0080

#define FCMP_OP_MASK      0x0007
#define FCMP_MODE_MASK    0x00F0

FilterExprNode *fop_cmp_new(LogTemplate *left, LogTemplate *right,
                            const gchar *type, gint compare_mode,
                            const gchar *location);

#endif
