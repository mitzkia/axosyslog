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

#ifndef FILTER_RE_H_INCLUDED
#define FILTER_RE_H_INCLUDED

#include "filter-expr.h"
#include "logmatcher.h"

LogMatcherOptions *filter_re_get_matcher_options(FilterExprNode *s);
gboolean filter_re_compile_pattern(FilterExprNode *s, const gchar *re, GError **error);

FilterExprNode *filter_re_new(NVHandle value_handle);
FilterExprNode *filter_source_new(void);

gboolean filter_match_is_usage_obsolete(FilterExprNode *s);
void filter_match_set_value_handle(FilterExprNode *s, NVHandle value_handle);
void filter_match_set_template_ref(FilterExprNode *s, LogTemplate *template);
FilterExprNode *filter_match_new(void);

#endif
