/*
 * Copyright (c) 2023 László Várady
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

/*
 * This code has been copied from NetBSD libc implementation with a
 * permissive license.
 */

/*-
 * Copyright (c) 2011 The NetBSD Foundation, Inc.
 * All rights reserved.
 *
 * This code is derived from software contributed to The NetBSD Foundation
 * by Christos Zoulas.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE NETBSD FOUNDATION, INC. AND CONTRIBUTORS
 * ``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
 * TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 * PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE FOUNDATION OR CONTRIBUTORS
 * BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 */

#include "compat/string.h"

#ifndef SYSLOG_NG_HAVE_GETLINE

#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>

ssize_t
getdelim(char **buf, size_t *bufsiz, int delimiter, FILE *fp)
{
  char *ptr, *eptr;


  if (*buf == NULL || *bufsiz == 0)
    {
      *bufsiz = BUFSIZ;
      if ((*buf = malloc(*bufsiz)) == NULL)
        return -1;
    }

  for (ptr = *buf, eptr = *buf + *bufsiz;;)
    {
      int c = fgetc(fp);
      if (c == -1)
        {
          if (feof(fp))
            {
              ssize_t diff = (ssize_t)(ptr - *buf);
              if (diff != 0)
                {
                  *ptr = '\0';
                  return diff;
                }
            }
          return -1;
        }
      *ptr++ = c;
      if (c == delimiter)
        {
          *ptr = '\0';
          return ptr - *buf;
        }
      if (ptr + 2 >= eptr)
        {
          char *nbuf;
          size_t nbufsiz = *bufsiz * 2;
          ssize_t d = ptr - *buf;
          if ((nbuf = realloc(*buf, nbufsiz)) == NULL)
            return -1;
          *buf = nbuf;
          *bufsiz = nbufsiz;
          eptr = nbuf + nbufsiz;
          ptr = nbuf + d;
        }
    }
}

ssize_t
getline(char **buf, size_t *bufsiz, FILE *fp)
{
  return getdelim(buf, bufsiz, '\n', fp);
}

#endif
