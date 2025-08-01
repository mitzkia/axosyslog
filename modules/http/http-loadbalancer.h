/*
 * Copyright (c) 2018 Balazs Scheidler
 * Copyright (c) 2018 Balabit
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

#ifndef HTTP_LOADBALANCER_H_INCLUDED
#define HTTP_LOADBALANCER_H_INCLUDED 1

#include "template/templates.h"

typedef enum
{
  HTTP_TARGET_OPERATIONAL,
  HTTP_TARGET_FAILED
} HTTPLoadBalancerTargetState;

typedef struct _HTTPLoadBalancerTarget HTTPLoadBalancerTarget;
typedef struct _HTTPLoadBalancerClient HTTPLoadBalancerClient;
typedef struct _HTTPLoadBalancer HTTPLoadBalancer;


/* NOTE: this struct represents an actual HTTP target URL.  The existence of
 * this structure is ensured even in multi-threaded environments.  Some of
 * the members of the struct are read-only and are _always_ available
 * without locking.  Others are protected by the LoadBalancer's lock and
 * should be manipulated under the protection of that lock.
 */
struct _HTTPLoadBalancerTarget
{
  /* read-only data, no need to lock */
  LogTemplate *url_template;
  gint index;
  /* read-write data, locking must be in effect */
  HTTPLoadBalancerTargetState state;
  gint number_of_clients;
  gint max_clients;
  time_t last_failure_time;
  gchar formatted_index[16];
};

gboolean http_lb_target_is_url_templated(HTTPLoadBalancerTarget *self);
const gchar *http_lb_target_get_literal_url(HTTPLoadBalancerTarget *self);
void http_lb_target_format_templated_url(HTTPLoadBalancerTarget *self, LogMessage *msg,
                                         const LogTemplateOptions *template_options, GString *result);

struct _HTTPLoadBalancerClient
{
  HTTPLoadBalancerTarget *target;
};

void http_lb_client_init(HTTPLoadBalancerClient *, HTTPLoadBalancer *lb);
void http_lb_client_deinit(HTTPLoadBalancerClient *);

struct _HTTPLoadBalancer
{
  GMutex lock;
  HTTPLoadBalancerTarget *targets;
  gint num_targets;
  gint num_clients;
  gint num_failed_targets;
  gint recovery_timeout;
  time_t last_recovery_attempt;
};

HTTPLoadBalancerTarget *http_load_balancer_choose_target(HTTPLoadBalancer *self, HTTPLoadBalancerClient *lbc);
gboolean http_load_balancer_add_target(HTTPLoadBalancer *self, const gchar *url, GError **error);
void http_load_balancer_drop_all_targets(HTTPLoadBalancer *self);
void http_load_balancer_track_client(HTTPLoadBalancer *self, HTTPLoadBalancerClient *lbc);
void http_load_balancer_set_target_failed(HTTPLoadBalancer *self, HTTPLoadBalancerTarget *target);
void http_load_balancer_set_target_successful(HTTPLoadBalancer *self, HTTPLoadBalancerTarget *target);
gboolean http_load_balancer_is_url_templated(HTTPLoadBalancer *self);

void http_load_balancer_set_recovery_timeout(HTTPLoadBalancer *self, gint recovery_timeout);
HTTPLoadBalancer *http_load_balancer_new(void);
void http_load_balancer_free(HTTPLoadBalancer *self);



#endif
