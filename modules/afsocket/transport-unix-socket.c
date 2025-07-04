/*
 * Copyright (c) 2002-2014 Balabit
 * Copyright (c) 1998-2013 Balázs Scheidler
 * Copyright (c) 2014 Gergely Nagy
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
#include "transport-unix-socket.h"
#include "transport/transport-socket.h"
#include "scratch-buffers.h"
#include "str-format.h"
#include "compat-unix-creds.h"
#include "messages.h"

#include <sys/types.h>
#include <sys/stat.h>
#include <sys/socket.h>
#include <fcntl.h>
#include <errno.h>
#include <string.h>
#include <unistd.h>

static void G_GNUC_UNUSED
_add_nv_pair_int(LogTransportAuxData *aux, const gchar *name, gint value)
{
  ScratchBuffersMarker marker;
  GString *buf = scratch_buffers_alloc_and_mark(&marker);

  g_string_truncate(buf, 0);
  format_uint32_padded(buf, -1, 0, 10, value);
  log_transport_aux_data_add_nv_pair(aux, name, buf->str);
  scratch_buffers_reclaim_marked(marker);
}

static void
_format_proc_file_name(gchar *buf, gsize buflen, pid_t pid, const gchar *proc_file)
{
  g_snprintf(buf, buflen, "/proc/%d/%s", pid, proc_file);
}

static gssize
_read_text_file_content(const gchar *filename, gchar *buf, gsize buflen)
{
  gint fd;
  gssize rc;
  gssize pos = 0;

  fd = open(filename, O_RDONLY);
  if (fd < 0)
    return -1;
  rc = 1;

  /* this loop leaves the last character of buf untouched, thus -1 in the
   * condition and the number of bytes to be read */
  while (rc > 0 && pos < buflen - 1)
    {
      gsize count = (buflen - 1) - pos;

      rc = read(fd, buf + pos, count);
      if (rc < 0)
        {
          close(fd);
          return -1;
        }
      pos += rc;
    }

  /* zero terminate the buffer */
  buf[pos] = 0;
  close(fd);
  return pos;
}

static gssize
_read_text_file_content_without_trailing_newline(const gchar *filename, gchar *buf, gsize buflen)
{
  gssize content_len;

  content_len = _read_text_file_content(filename, buf, buflen);
  if (content_len <= 0)
    return content_len;
  if (buf[content_len - 1] == '\n')
    content_len--;
  buf[content_len] = 0;
  return content_len;
}


static void G_GNUC_UNUSED
_add_nv_pair_proc_read_unless_unset(LogTransportAuxData *aux, const gchar *name, pid_t pid, const gchar *proc_file,
                                    const gchar *unset_value)
{
  gchar filename[64];
  gchar content[4096];
  gssize content_len;

  _format_proc_file_name(filename, sizeof(filename), pid, proc_file);
  content_len = _read_text_file_content_without_trailing_newline(filename, content, sizeof(content));
  if (content_len > 0 && (!unset_value || strcmp(content, unset_value) != 0))
    log_transport_aux_data_add_nv_pair(aux, name, content);
}

static void G_GNUC_UNUSED
_add_nv_pair_proc_read_argv(LogTransportAuxData *aux, const gchar *name, pid_t pid, const gchar *proc_file)
{
  gchar filename[64];
  gchar content[4096];
  gssize content_len;
  gint i;

  _format_proc_file_name(filename, sizeof(filename), pid, proc_file);
  content_len = _read_text_file_content(filename, content, sizeof(content));

  for (i = 0; i < content_len; i++)
    {
      if (!g_ascii_isprint(content[i]))
        content[i] = ' ';
    }
  if (content_len > 0)
    log_transport_aux_data_add_nv_pair(aux, name, content);
}

static void G_GNUC_UNUSED
_add_nv_pair_proc_readlink(LogTransportAuxData *aux, const gchar *name, pid_t pid, const gchar *proc_file)
{
  gchar filename[64];
  gchar content[4096];
  gssize content_len;

  _format_proc_file_name(filename, sizeof(filename), pid, proc_file);
  content_len = readlink(filename, content, sizeof(content));
  if (content_len > 0)
    {
      if (content_len == sizeof(content))
        content_len--;
      content[content_len] = 0;
      log_transport_aux_data_add_nv_pair(aux, name, content);
    }
}

#if defined (CRED_PASS_SUPPORTED)
static void
_feed_aux_from_ucred(LogTransportAuxData *aux, cred_t *uc)
{
  _add_nv_pair_int(aux, ".unix.pid", cred_get(uc, pid));
  _add_nv_pair_int(aux, ".unix.uid", cred_get(uc, uid));
  _add_nv_pair_int(aux, ".unix.gid", cred_get(uc, gid));
}
#endif

#if defined(__linux__) && defined(CRED_PASS_SUPPORTED)
static void
_feed_aux_from_procfs(LogTransportAuxData *aux, pid_t pid)
{
  _add_nv_pair_proc_read_argv(aux, ".unix.cmdline", pid, "cmdline");
  _add_nv_pair_proc_readlink(aux, ".unix.exe", pid, "exe");
  /* NOTE: we use the names the audit subsystem does, so if in the future we'd be
   * processing audit records, the nvpair names would match up. */
  _add_nv_pair_proc_read_unless_unset(aux, ".audit.auid", pid, "loginuid", "4294967295");
  _add_nv_pair_proc_read_unless_unset(aux, ".audit.ses", pid, "sessionid", "4294967295");
}

#elif defined(__FreeBSD__) && defined(CRED_PASS_SUPPORTED)
static void
_feed_aux_from_procfs(LogTransportAuxData *aux, pid_t pid)
{
  _add_nv_pair_proc_read_argv(aux, ".unix.cmdline", pid, "cmdline");
  _add_nv_pair_proc_readlink(aux, ".unix.exe", pid, "file");
}
#endif

static void
_parse_cmsg(LogTransportSocket *s, struct cmsghdr *cmsg, LogTransportAuxData *aux)
{
#if defined(CRED_PASS_SUPPORTED)
  cred_t uc;

  if (cmsg->cmsg_level == SOL_SOCKET && cmsg->cmsg_type == SCM_CREDENTIALS)
    {
      memcpy(&uc, CMSG_DATA(cmsg), sizeof(uc));

      _feed_aux_from_procfs(aux, cred_get(&uc, pid));
      _feed_aux_from_ucred(aux, &uc);
    }
#endif
  log_transport_socket_parse_cmsg_method(s, cmsg, aux);
}

LogTransport *
log_transport_unix_dgram_socket_new(gint fd)
{
  LogTransportSocket *self = g_new0(LogTransportSocket, 1);

  log_transport_dgram_socket_init_instance(self, fd);
  self->parse_cmsg = _parse_cmsg;
  return &self->super;
}

LogTransport *
log_transport_unix_stream_socket_new(gint fd)
{
  LogTransportSocket *self = g_new0(LogTransportSocket, 1);

  log_transport_stream_socket_init_instance(self, fd);
  self->parse_cmsg = _parse_cmsg;

  return &self->super;
}
