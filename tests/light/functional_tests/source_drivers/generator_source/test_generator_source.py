#!/usr/bin/env python
#############################################################################
# Copyright (c) 2019 Balabit
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

from functional_tests.conftest import get_log_message_for_performance_test
from src.common.blocking import wait_until_true

def test_generator_source(config, syslog_ng):
    generator_source = config.create_example_msg_generator_source(num=1)
    file_destination = config.create_file_destination(file_name="output.log", template="'$MSG\n'")

    config.create_logpath(statements=[generator_source, file_destination])
    syslog_ng.start(config)
    log = file_destination.read_log()
    assert log == generator_source.DEFAULT_MESSAGE + "\n"

def generate_unicode_char():
    unicode_chars = []
    us = u""
    counter = 0
    for i in range(0,1114111):
        counter += 1
        us += chr(i)
        if counter == 1000:
            unicode_chars.append(us)
            counter = 0
            us = u""
    return unicode_chars

@pytest.mark.parametrize("unicode_char", generate_unicode_char())
def test_generator_source_all_unicode_chars(config, syslog_ng, syslog_ng_ctl, unicode_char):
    generator_source = config.create_example_msg_generator_source(freq=0.1, num=10, template="'%s'" % unicode_char)
    file_destination = config.create_file_destination(file_name="output.log")

    config.create_logpath(statements=[generator_source, file_destination])
    syslog_ng.start(config)
    syslog_ng.reload(config)
    syslog_ng_ctl.stats()
    # log = file_destination.read_log()
    # print("%s\n" % log)
    # assert log == generator_source.DEFAULT_MESSAGE + "\n"


@pytest.mark.performance
def test_generator_source_performance(config, syslog_ng):
    generator_source = config.create_example_msg_generator_source(freq=0.0001, template="'%s'" % get_log_message_for_performance_test())
    config, source_driver, destination_driver = config.set_perf_test_config(config, generator_source)

    syslog_ng.start(config, stderr=False, debug=False, trace=False, verbose=False)
    wait_until_true(lambda: "processed" in destination_driver.get_stats())

    MSG_COUNT = 10000000 # 5M
    # while ((destination_driver.get_stats()["eps_last_1h"] <= 0) and ( destination_driver.get_stats()["processed"] <= MSG_COUNT)):
    while (( destination_driver.get_stats()["processed"] <= MSG_COUNT)):
        time.sleep(5)
        print("Actual processed msg count: %s, expected msg count: %s" % (destination_driver.get_stats()["processed"], MSG_COUNT))

    print(source_driver.get_stats())
    print(destination_driver.get_stats())
