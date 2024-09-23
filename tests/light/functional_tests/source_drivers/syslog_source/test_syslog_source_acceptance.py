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

import pytest

from src.common.blocking import wait_until_true
from functional_tests.parametrize_smoke_testcases import generate_id_name
from functional_tests.parametrize_smoke_testcases import generate_options_and_values_for_driver


def test_syslog_source_acceptance(config, syslog_ng, log_message, port_allocator, loggen, syslog_formatter):
    input_message = syslog_formatter.format_message(log_message)
    syslog_source = config.create_syslog_source(ip="localhost", port=port_allocator())
    file_destination = config.create_file_destination(file_name="output.log")
    config.create_logpath(statements=[syslog_source, file_destination])
    
    syslog_ng.start(config)
    syslog_source.write_log(input_message)

    # loggen.start(syslog_source.options["ip"], syslog_source.options["port"], size=256, inet=True, stream=True, syslog_proto=True, number=NUMBER_OF_MESSAGES)
    # wait_until_true(lambda: loggen.get_sent_message_count() == NUMBER_OF_MESSAGES)

    print("\n[%s]" % file_destination.read_log())

@pytest.mark.performance
def test_syslog_source_performance(config, syslog_ng, port_allocator, loggen):
    syslog_source = config.create_syslog_source(ip="localhost", port=port_allocator())
    config, source_driver, destination_driver = config.set_perf_test_config(config, syslog_source)
    
    syslog_ng.start(config, stderr=False, debug=False, trace=False, verbose=False)
    wait_until_true(lambda: "connections" in source_driver.get_stats())

    NUMBER_OF_MESSAGES = 9000000
    loggen.start(source_driver.options["ip"], source_driver.options["port"], inet=True, stream=True, size=250, number=NUMBER_OF_MESSAGES, interval=130, rate=10000000, syslog_proto=True)
    wait_until_true(lambda: "processed" in destination_driver.get_stats())

    while ( destination_driver.get_stats()["processed"] <= NUMBER_OF_MESSAGES):
        time.sleep(5)
        print("Actual processed msg count: %s, expected msg count: %s" % (destination_driver.get_stats()["processed"], NUMBER_OF_MESSAGES))

    print(source_driver.get_stats())
    print(destination_driver.get_stats())


@pytest.mark.parametrize("option_and_value", generate_options_and_values_for_driver("source", "syslog"), ids=generate_id_name)
def test_syslog_source_options(config, syslog_ng, port_allocator, option_and_value):
    syslog_source = config.create_syslog_source(ip="localhost", port=port_allocator(), **option_and_value)
    file_destination = config.create_file_destination(file_name="output.log")
    config.create_logpath(statements=[syslog_source, file_destination])
    
    syslog_ng.start(config)
    wait_until_true(lambda: "connections" in syslog_source.get_stats())

    # print("\n[%s]" % file_destination.read_log())
    syslog_ng.stop()