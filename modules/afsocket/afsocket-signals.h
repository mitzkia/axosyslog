/*
 * Copyright (c) 2023 Balazs Scheidler <bazsi77@gmail.com>
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

#ifndef AFSOCKET_SIGNALS_H_INCLUDED
#define AFSOCKET_SIGNALS_H_INCLUDED

#include "signal-slot-connector/signal-slot-connector.h"
#include "transport/tls-context.h"

typedef struct _AFSocketTLSCertificateValidationSignalData
{
  TLSContext *tls_context;
  X509_STORE_CTX *ctx;
  gboolean failure;
} AFSocketTLSCertificateValidationSignalData;

typedef struct _AFSocketSetupSocketSignalData
{
  gint sock;
  /* initialized to FALSE by the caller, must be set to TRUE in order to
   * fail the initialization */
  gboolean failure;
} AFSocketSetupSocketSignalData;

#define signal_afsocket_setup_socket SIGNAL(afsocket, setup_socket, AFSocketSetupSocketSignalData *)

#define signal_afsocket_tls_certificate_validation SIGNAL(afsocket, tls_certificate_validation, AFSocketTLSCertificateValidationSignalData *)

#endif
