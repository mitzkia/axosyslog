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

from functional_tests.conftest import get_log_message_for_performance_test
from src.common.blocking import wait_until_true
from src.common.file import copy_shared_file
from src.executors.command_executor import CommandExecutor

input_log = "<38>Feb 11 21:27:22 testhost testprogram[9999]: test message\n"
expected_log = "Feb 11 21:27:22 testhost testprogram[9999]: test message\n"


@pytest.mark.parametrize(
    "input_log, expected_log, counter", [
        (input_log, expected_log, 1),
        (input_log, expected_log, 10),
    ], ids=["with_one_log", "with_ten_logs"],
)
def test_acceptance(config, syslog_ng, syslog_ng_ctl, input_log, expected_log, counter):
    file_source = config.create_file_source(file_name="input.log")
    file_destination = config.create_file_destination(file_name="output.log")
    config.create_logpath(statements=[file_source, file_destination])
    config.update_global_options(keep_hostname="yes")

    file_source.write_log(input_log, counter)
    syslog_ng.start(config)
    assert file_destination.read_logs(counter) == [expected_log] * counter


def test_wildcard_file_source_default(config, syslog_ng, syslog_ng_ctl):
    config.update_global_options(stats_level=5)
    wildcard_file_source = config.create_wildcard_file_source(base_dir="aaa/bbbb/", filename_pattern="almafa*.log")
    file_destination = config.create_file_destination(file_name="output.log")
    config.create_logpath(statements=[wildcard_file_source, file_destination])
    config.update_global_options(keep_hostname="yes")

    wildcard_file_source.generate_paths_for_wildcard_pattern(3)

    wildcard_file_source.write_log(input_log, 2)
    syslog_ng.start(config)
    assert file_destination.read_logs(2) == [expected_log] * 2
    print(file_destination.get_stats())
    print(wildcard_file_source.get_stats())
    assert wildcard_file_source.get_stats()["processed"] == 6


def test_read_kernel_log(config, syslog_ng, testcase_parameters):
    file_source = config.create_file_source(file_name="/dev/kmsg", program_override="kernel", flags="kernel")
    file_destination = config.create_file_destination(file_name="output.log", template="'$(format-json --scope everything)\n'")
    config.create_logpath(statements=[file_source, file_destination])
    config.update_global_options(stats="level(1)")

    copy_shared_file(testcase_parameters, "do_nothing.sh")

    command_executor = CommandExecutor()
    command = ["./do_nothing.sh"]

    command_executor.run(command, "/tmp/do_nothing_stdout", "/tmp/do_nothing_stderr", detach=True)

    syslog_ng.start(config)

    command_executor.run(["pkill", "-11", "do_nothing.sh"], "/tmp/pkill_stdout", "/tmp/pkill_stderr")
    command_executor.run(["pkill", "-11", "sleep"], "/tmp/pkill_stdout", "/tmp/pkill_stderr")

    assert file_destination.read_until_logs(["potentially unexpected fatal signal 11"])
    
    assert file_destination.get_stats()["written"] > 0

@pytest.mark.performance
def test_file_source_performance(config, syslog_ng):

    file_source = config.create_file_source(file_name="big_log.txt")
    config, source_driver, destination_driver = config.set_perf_test_config(config, file_source)

    MSG_COUNT = 5000000 # 7M
    with open("big_log.txt", "a+") as big_file_object:
        big_file_object.write(get_log_message_for_performance_test()*MSG_COUNT)

    syslog_ng.start(config, stderr=False, debug=False, trace=False, verbose=False)
    wait_until_true(lambda: "processed" in destination_driver.get_stats())

    while (destination_driver.get_stats()["processed"] != MSG_COUNT):
        time.sleep(5)
        print("Actual processed msg count: %s, expected msg count: %s" % (destination_driver.get_stats()["processed"], MSG_COUNT))

    print(source_driver.get_stats())
    print(destination_driver.get_stats())
