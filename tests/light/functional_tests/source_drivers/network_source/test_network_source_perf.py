#!/usr/bin/env python
#############################################################################
# Copyright (c) 2020 One Identity
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

import pytest

from src.common.blocking import wait_until_true


@pytest.mark.performance
def test_network_source_performance(config, syslog_ng, loggen, port_allocator):
    network_source = config.create_network_source(ip="localhost", port=port_allocator(), )
    config, source_driver, destination_driver = config.set_perf_test_config(config, network_source)

    syslog_ng.start(config, stderr=False, debug=False, trace=False, verbose=False)
    wait_until_true(lambda: "connections" in source_driver.get_stats())

    NUMBER_OF_MESSAGES = 3000000
    loggen.start(source_driver.options["ip"], source_driver.options["port"], inet=True, stream=True, size=250, number=NUMBER_OF_MESSAGES, interval=130, rate=10000000)
    wait_until_true(lambda: "processed" in destination_driver.get_stats())

    while (destination_driver.get_stats()["processed"] != NUMBER_OF_MESSAGES):
        time.sleep(5)
        print("Actual processed msg count: %s, expected msg count: %s" % (destination_driver.get_stats()["processed"], NUMBER_OF_MESSAGES))

    print(source_driver.get_stats())
    print(destination_driver.get_stats())
