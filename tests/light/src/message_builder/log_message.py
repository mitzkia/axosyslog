# -*- coding: utf-8 -*-
#!/usr/bin/env python
#############################################################################
# Copyright (c) 2015-2018 Balabit
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
# As an additional exemption you are allowed to compile & link against the
# OpenSSL libraries as published by the OpenSSL project. See the file
# COPYING for details.
#
#############################################################################
import time


class LogMessage(object):
    def __init__(self):
        self.priority_value = "38"
        self.syslog_protocol_version = "1"
        self.timestamp_value = time.time()
        self.bsd_timestamp_value = "Feb 11 21:27:22"
        self.iso_timestamp_value = "2024-09-15T03:34:57+00:00"
        self.hostname_value = "localhost"
        self.program_value = "prg00000"
        self.pid_value = "1234"
        self.message_id = "-"
        self.sdata = '-'
        self.message_value = u"seq: 0000000000, thread: 0000, runid: 1726371297, stamp: 2024-09-15T03:34:57 üóöóüűáéÚŐÁÉŰÖÜÖÓ"

    def priority(self, pri):
        self.priority_value = pri
        return self

    def remove_priority(self):
        self.priority_value = ""
        return self

    def syslog_protocol_version(self, protocol_version):
        self.syslog_protocol_version = protocol_version
        return self

    def timestamp(self, timestamp):
        self.timestamp_value = timestamp
        return self

    def hostname(self, hostname):
        self.hostname_value = hostname
        return self

    def program(self, program):
        self.program_value = program
        return self

    def pid(self, pid):
        self.pid_value = pid
        return self

    def message_id(self, msg_id):
        self.message_id = msg_id
        return self

    def sdata(self, sdata):
        self.sdata = sdata
        return self

    def message(self, message):
        self.message_value = message
        return self
