#!/usr/bin/env python
#############################################################################
# Copyright (c) 2025 Andras Mitzki <andras.mitzki@axoflow.com>
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# As an additional exemption you are allowed to compile & link against the
# OpenSSL libraries as published by the OpenSSL project. See the file
# COPYING for details.
#
#############################################################################


def test_clickhouse_destination(config, syslog_ng, port_allocator):
    generator_source = config.create_example_msg_generator_source(num=1)
    clickhouse_destination = config.create_clickhouse_destination(database="test_db", table="test_table", user="test_user", schema='"MESSAGE" => "$MSG"')

    config.create_logpath(statements=[generator_source, clickhouse_destination])
    syslog_ng.start(config)
    import time
    time.sleep(5)
    syslog_ng.stop()
    # log = file_destination.read_log()
    # assert log == generator_source.DEFAULT_MESSAGE
