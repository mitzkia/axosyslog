/*
 * Copyright (c) 2002-2012 Balabit
 * Copyright (c) 1998-2012 Balázs Scheidler
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

#include "logpipe.h"
#include "cfg-tree.h"
#include "perf/perf.h"

gboolean (*pipe_single_step_hook)(LogPipe *pipe, LogMessage *msg, const LogPathOptions *path_options);

void
log_pipe_forward_msg(LogPipe *self, LogMessage *msg, const LogPathOptions *path_options)
{
  if (self->pipe_next)
    {
      log_pipe_queue(self->pipe_next, msg, path_options);
    }
  else
    {
      log_msg_drop(msg, path_options, AT_PROCESSED);
    }
}

/*
 * LogPipeQueue slow path that can potentially change "msg" and
 * "path_options", causing tail call optimization to be disabled.
 */
static void
log_pipe_queue_slow_path(LogPipe *self, LogMessage *msg, const LogPathOptions *path_options)
{
  LogPathOptions local_path_options;
  if ((self->flags & PIF_SYNC_FILTERX_TO_MSG))
    filterx_eval_sync_message(path_options->filterx_context, &msg, path_options);

  if (G_UNLIKELY(self->flags &
                 (PIF_HARD_FLOW_CONTROL | PIF_NO_HARD_FLOW_CONTROL | PIF_JUNCTION_END | PIF_CONDITIONAL_MIDPOINT)))
    {
      path_options = log_path_options_chain(&local_path_options, path_options);
      if (self->flags & PIF_HARD_FLOW_CONTROL)
        {
          local_path_options.flow_control_requested = TRUE;
          msg_trace("Enabling flow control", log_pipe_location_tag(self), evt_tag_msg_reference(msg));
        }
      if (self->flags & PIF_NO_HARD_FLOW_CONTROL)
        {
          local_path_options.flow_control_requested = FALSE;
          msg_trace("Disabling flow control", log_pipe_location_tag(self), evt_tag_msg_reference(msg));
        }
      if (self->flags & PIF_JUNCTION_END)
        {
          log_path_options_pop_junction(&local_path_options);
        }
      if (self->flags & PIF_CONDITIONAL_MIDPOINT)
        {
          log_path_options_pop_conditional(&local_path_options);
        }
    }
  self->queue(self, msg, path_options);
}

static inline gboolean
_is_fastpath(LogPipe *self)
{
  if (self->flags & PIF_SYNC_FILTERX_TO_MSG)
    return FALSE;

  if (self->flags & (PIF_HARD_FLOW_CONTROL | PIF_NO_HARD_FLOW_CONTROL | PIF_JUNCTION_END | PIF_CONDITIONAL_MIDPOINT))
    return FALSE;

  return TRUE;
}

void
log_pipe_queue(LogPipe *self, LogMessage *msg, const LogPathOptions *path_options)
{
  g_assert((self->flags & PIF_INITIALIZED) != 0);

  if (G_UNLIKELY((self->flags & PIF_CONFIG_RELATED) != 0 && pipe_single_step_hook))
    {
      if (!pipe_single_step_hook(self, msg, path_options))
        {
          log_msg_drop(msg, path_options, AT_PROCESSED);
          return;
        }
    }

  /* on the fastpath we can use tail call optimization, so we won't have a
   * series of log_pipe_queue() calls on the stack, it improves perf traces
   * if nothing else, but I believe it also helps locality by using a lot
   * less stack space */
  if (_is_fastpath(self))
    self->queue(self, msg, path_options);
  else
    log_pipe_queue_slow_path(self, msg, path_options);
}


EVTTAG *
log_pipe_location_tag(LogPipe *pipe)
{
  return log_expr_node_location_tag(pipe->expr_node);
}

void
log_pipe_attach_expr_node(LogPipe *self, LogExprNode *expr_node)
{
  self->expr_node = log_expr_node_ref(expr_node);
}

void
log_pipe_detach_expr_node(LogPipe *self)
{
  if (!self->expr_node)
    return;
  log_expr_node_unref(self->expr_node);
  self->expr_node = NULL;
}

void
log_pipe_walk_method(LogPipe *self, LogPathWalkFunc func, gpointer user_data)
{
  if (self->pipe_next)
    {
      if (func(self, PIW_PIPE_NEXT, self->pipe_next, user_data))
        log_pipe_walk(self->pipe_next, func, user_data);
    }
}

void
log_pipe_clone_method(LogPipe *dst, const LogPipe *src)
{
  log_pipe_set_persist_name(dst, src->persist_name);
  log_pipe_set_options(dst, &src->options);
}

gboolean
log_pipe_pre_config_init_method(LogPipe *self)
{
  return TRUE;
}

gboolean
log_pipe_post_config_init_method(LogPipe *self)
{
  if ((self->flags & PIF_CONFIG_RELATED) && perf_is_enabled())
    {
      gchar buf[256];

      self->queue = perf_generate_trampoline(self->queue, log_expr_node_format_location(self->expr_node, buf, sizeof(buf)));
    }
  return TRUE;
}

void
log_pipe_init_instance(LogPipe *self, GlobalConfig *cfg)
{
  g_atomic_counter_set(&self->ref_cnt, 1);
  self->cfg = cfg;
  self->pipe_next = NULL;
  self->persist_name = NULL;
  self->plugin_name = NULL;
  self->pre_config_init = log_pipe_pre_config_init_method;
  self->post_config_init = log_pipe_post_config_init_method;
  self->queue = log_pipe_forward_msg;
  self->free_fn = log_pipe_free_method;
  self->walk = log_pipe_walk_method;
}

LogPipe *
log_pipe_new(GlobalConfig *cfg)
{
  LogPipe *self = g_new0(LogPipe, 1);

  log_pipe_init_instance(self, cfg);
  return self;
}

void
log_pipe_free_method(LogPipe *self)
{
  ;
}

LogPipe *
log_pipe_ref(LogPipe *self)
{
  g_assert(!self || g_atomic_counter_get(&self->ref_cnt) > 0);

  if (self)
    {
      g_atomic_counter_inc(&self->ref_cnt);
    }
  return self;
}

static void
_free(LogPipe *self)
{
  if (self->free_fn)
    self->free_fn(self);
  g_free((gpointer)self->persist_name);
  g_free(self->plugin_name);
  g_list_free_full(self->info, g_free);
  g_free(self);
}

gboolean
log_pipe_unref(LogPipe *self)
{
  g_assert(!self || g_atomic_counter_get(&self->ref_cnt));

  if (self && (g_atomic_counter_dec_and_test(&self->ref_cnt)))
    {
      _free(self);
      return TRUE;
    }

  return FALSE;
}

void
log_pipe_forward_notify(LogPipe *self, gint notify_code, gpointer user_data)
{
  log_pipe_notify(self->pipe_next, notify_code, user_data);
}

void
log_pipe_set_persist_name(LogPipe *self, const gchar *persist_name)
{
  g_free((gpointer)self->persist_name);
  self->persist_name = g_strdup(persist_name);
}

const gchar *
log_pipe_get_persist_name(const LogPipe *self)
{
  return (self->generate_persist_name != NULL) ? self->generate_persist_name(self)
         : self->persist_name;
}

void
log_pipe_set_options(LogPipe *self, const LogPipeOptions *options)
{
  self->options = *options;
}

void
log_pipe_set_internal(LogPipe *self, gboolean internal)
{
  self->options.internal = internal;
}

gboolean
log_pipe_is_internal(const LogPipe *self)
{
  return self->options.internal;
}

void
log_pipe_add_info(LogPipe *self, const gchar *info)
{
  self->info = g_list_append(self->info, g_strdup(info));
}

#ifdef __linux__

void
__log_pipe_forward_msg(LogPipe *self, LogMessage *msg, const LogPathOptions *path_options)
__attribute__((alias("log_pipe_forward_msg")));

#endif
