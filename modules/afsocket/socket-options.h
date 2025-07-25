/*
 * Copyright (c) 2002-2014 Balabit
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
#ifndef SOCKET_OPTIONS_H_INCLUDED
#define SOCKET_OPTIONS_H_INCLUDED

#include "gsockaddr.h"

typedef enum
{
  AFSOCKET_DIR_RECV = 0x01,
  AFSOCKET_DIR_SEND = 0x02,
} AFSocketDirection;

typedef struct _SocketOptions SocketOptions;

struct _SocketOptions
{
  /* socket options */
  gint so_sndbuf;
  gint so_rcvbuf;
  gint so_broadcast;
  gint so_keepalive;
  gboolean so_reuseport;
  gboolean (*setup_socket)(SocketOptions *s, gint sock, GSockAddr *bind_addr, AFSocketDirection dir);
  gboolean (*setup_peer_socket)(SocketOptions *s, gint sock, GSockAddr *peer_addr);
  void (*free)(gpointer s);
};

gboolean socket_options_setup_socket_method(SocketOptions *self, gint fd, GSockAddr *bind_addr, AFSocketDirection dir);
gboolean socket_options_setup_peer_socket_method(SocketOptions *self, gint fd, GSockAddr *bind_addr);
void socket_options_init_instance(SocketOptions *self);
SocketOptions *socket_options_new(void);

static inline gboolean
socket_options_setup_socket(SocketOptions *s, gint sock, GSockAddr *bind_addr, AFSocketDirection dir)
{
  return s->setup_socket(s, sock, bind_addr, dir);
}

static inline gboolean
socket_options_setup_peer_socket(SocketOptions *s, gint sock, GSockAddr *peer_addr)
{
  return s->setup_peer_socket(s, sock, peer_addr);
}

static inline void
socket_options_free(SocketOptions *s)
{
  s->free(s);
}

#endif
