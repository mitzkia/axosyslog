/*
 * Copyright (c) 2002-2014 Balabit
 * Copyright (c) 2014 Laszlo Budai
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

#ifndef ACK_TRACKER_H_INCLUDED
#define ACK_TRACKER_H_INCLUDED

#include "syslog-ng.h"
#include "logsource.h"
#include "ack_tracker_types.h"
#include "bookmark.h"

struct _AckTracker
{
  LogSource *source;
  Bookmark *(*request_bookmark)(AckTracker *self);
  void (*track_msg)(AckTracker *self, LogMessage *msg);
  void (*manage_msg_ack)(AckTracker *self, LogMessage *msg, AckType ack_type);
  void (*free_fn)(AckTracker *self);
  void (*disable_bookmark_saving)(AckTracker *self);
  gboolean (*init)(AckTracker *self);
  void (*deinit)(AckTracker *self);
};

struct _AckRecord
{
  AckTracker *tracker;
  Bookmark bookmark;
};

static inline void
ack_tracker_free(AckTracker *self)
{
  if (self && self->free_fn)
    {
      self->free_fn(self);
    }
}

static inline Bookmark *
ack_tracker_request_bookmark(AckTracker *self)
{
  return self->request_bookmark(self);
}

static inline void
ack_tracker_track_msg(AckTracker *self, LogMessage *msg)
{
  self->track_msg(self, msg);
}

static inline void
ack_tracker_manage_msg_ack(AckTracker *self, LogMessage *msg, AckType ack_type)
{
  self->manage_msg_ack(self, msg, ack_type);
}

static inline void
ack_tracker_disable_bookmark_saving(AckTracker *self)
{
  if (self->disable_bookmark_saving)
    {
      self->disable_bookmark_saving(self);
    }
}

static inline gboolean
ack_tracker_init(AckTracker *self)
{
  if (self && self->init)
    return self->init(self);

  return TRUE;
}

static inline void
ack_tracker_deinit(AckTracker *self)
{
  if (self && self->deinit)
    self->deinit(self);
}

#endif
