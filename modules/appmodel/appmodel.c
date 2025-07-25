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
#include "appmodel.h"
#include "cfg.h"
#include "appmodel-context.h"

#define MODULE_CONFIG_KEY "appmodel"

AppModelContext *
appmodel_get_context(GlobalConfig *cfg)
{
  AppModelContext *ac = g_hash_table_lookup(cfg->module_config, MODULE_CONFIG_KEY);
  if (!ac)
    {
      ac = appmodel_context_new();
      g_hash_table_insert(cfg->module_config, g_strdup(MODULE_CONFIG_KEY), ac);
    }
  return ac;
}

void
appmodel_register_application(GlobalConfig *cfg, Application *application)
{
  AppModelContext *ac = appmodel_get_context(cfg);

  appmodel_context_register_object(ac, &application->super);
}

void
appmodel_iter_applications(GlobalConfig *cfg, void (*foreach)(Application *app, gpointer user_data), gpointer user_data)
{
  AppModelContext *appmodel = appmodel_get_context(cfg);
  appmodel_context_iter_objects(appmodel, APPLICATION_TYPE_NAME, (AppModelContextIterFunc) foreach, user_data);
}

void
appmodel_register_transformation(GlobalConfig *cfg, Transformation *transformation)
{
  AppModelContext *ac = appmodel_get_context(cfg);

  appmodel_context_register_object(ac, &transformation->super);
}

void
appmodel_iter_transformations(GlobalConfig *cfg, void (*foreach)(Transformation *transformation, gpointer user_data),
                              gpointer user_data)
{
  AppModelContext *appmodel = appmodel_get_context(cfg);
  appmodel_context_iter_objects(appmodel, TRANSFORMATION_TYPE_NAME, (AppModelContextIterFunc) foreach, user_data);
}
