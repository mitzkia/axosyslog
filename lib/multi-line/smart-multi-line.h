/*
 * Copyright (c) 2023 Balazs Scheidler <bazsi77@gmail.com>
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

#ifndef MULTI_LINE_SMART_MULTI_LINE_H_INCLUDED
#define MULTI_LINE_SMART_MULTI_LINE_H_INCLUDED

#include "multi-line/multi-line-logic.h"

MultiLineLogic *smart_multi_line_new(void);

void smart_multi_line_global_init(void);
void smart_multi_line_global_deinit(void);

#endif
