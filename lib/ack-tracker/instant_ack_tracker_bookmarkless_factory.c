/*
 * Copyright (c) 2020 One Identity
 * Copyright (c) 2020 Laszlo Budai
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

#include "ack_tracker_factory.h"
#include "instant_ack_tracker.h"

typedef struct _InstantAckTrackerBookmarklessFactory
{
  AckTrackerFactory super;
} InstantAckTrackerBookmarklessFactory;

static AckTracker *
_factory_create(AckTrackerFactory *s, LogSource *source)
{
  return instant_ack_tracker_bookmarkless_new(source);
}

static void
_factory_free(AckTrackerFactory *s)
{
  InstantAckTrackerBookmarklessFactory *self = (InstantAckTrackerBookmarklessFactory *)s;
  g_free(self);
}

static void
_init_instance(AckTrackerFactory *s)
{
  ack_tracker_factory_init_instance(s);

  s->create = _factory_create;
  s->free_fn = _factory_free;
  s->type = ACK_INSTANT_BOOKMARKLESS;
}

AckTrackerFactory *
instant_ack_tracker_bookmarkless_factory_new(void)
{
  InstantAckTrackerBookmarklessFactory *factory = g_new0(InstantAckTrackerBookmarklessFactory, 1);
  _init_instance(&factory->super);

  return &factory->super;
}
