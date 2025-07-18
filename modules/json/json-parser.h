/*
 * Copyright (c) 2011-2012 Balabit
 * Copyright (c) 2011-2012 Gergely Nagy <algernon@balabit.hu>
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
 */

#ifndef JSONPARSER_H_INCLUDED
#define JSONPARSER_H_INCLUDED

#include "parser/parser-expr.h"

void json_parser_set_extract_prefix(LogParser *s, const gchar *extract_prefix);
void json_parser_set_prefix(LogParser *p, const gchar *prefix);
void json_parser_set_marker(LogParser *p, const gchar *marker);
void json_parser_set_key_delimiter(LogParser *p, gchar delimiter);
LogParser *json_parser_new(GlobalConfig *cfg);

#endif
