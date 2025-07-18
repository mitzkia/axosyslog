/*
 * Copyright (c) 2017 Balabit
 * Copyright (c) 2017 Balazs Scheidler <balazs.scheidler@balabit.com>
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
#include <criterion/criterion.h>

#include "application.h"

Test(application, empty_application_can_be_created_and_freed)
{
  Application *app;

  app = application_new("foobar", "*");
  appmodel_object_free(&app->super);
}

Test(application, filter_can_be_set_and_queried)
{
  Application *app;
  const gchar *filter_expr = "'1' eq '1'";
  const gchar *filter_expr2 = "'2' eq '2'";

  app = application_new("foobar", "*");
  application_set_filter(app, filter_expr, NULL);
  cr_assert_str_eq(app->filter_expr, filter_expr);

  application_set_filter(app, filter_expr2, NULL);
  cr_assert_str_eq(app->filter_expr, filter_expr2);
  appmodel_object_free(&app->super);
}

Test(application, parser_can_be_set_and_queried)
{
  Application *app;
  const gchar *parser_expr = "kv-parser();";
  const gchar *parser_expr2 = "csv-parser();";

  app = application_new("foobar", "*");
  application_set_parser(app, parser_expr, NULL);
  cr_assert_str_eq(app->parser_expr, parser_expr);

  application_set_parser(app, parser_expr2, NULL);
  cr_assert_str_eq(app->parser_expr, parser_expr2);
  appmodel_object_free(&app->super);
}
