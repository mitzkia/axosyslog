#!/usr/bin/env python
#############################################################################
# Copyright (c) 2025 Axoflow
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
import pytest
from axosyslog_light.common.blocking import wait_until_true
from axosyslog_light.helpers.loggen.loggen import LoggenStartParams

# disk-buffer option variants:
# # - reliable: yes/no
# # - capacity-bytes: default/custom min/over max
# # - front-cache-size: default/custom 0/over max
# # - flow-control: enabled/disabled
# disk-buffer function variants:
# # - disk-buffer file creation
# # - disk-buffer stats reporting
# # - filling disk-buffer until full / not full
# # - fill only memory-portion of disk-buffer
# disk-buffer test validations:
# # - no message loss (if flow-control enabled)
# # - message loss acceptable (if flow-control disabled)
# # - no message duplication
# # - ctl-stats correctness
# # - prometheus metrics correctness
# # - message ordering
# # - disk-buffer file creation
# send:
#  - 0 log message
#  - 1 log message
#  - that many log messages that fills up the memory portion of the disk-buffer
#  - that many log messages that fills up the memory portion of the disk-buffer + 1
#  - that many log messages that fills up the whole disk-buffer
#  - that many log messages that fills up the whole disk-buffer + 1


@pytest.mark.parametrize(
    "option_capacity_bytes", [None, '0', '1', '10Mib', '99999'],
)
@pytest.mark.parametrize(
    "option_front_cache_size", [None, '0', '1', '1000', '99999'],
)
@pytest.mark.parametrize(
    "option_flow_controll", [True, False],
)
def test_disk_buffer_acceptance(config, syslog_ng, port_allocator, option_capacity_bytes, option_front_cache_size, option_flow_controll, loggen):
    config.update_global_options(stats_level=5)
    network_source = config.create_network_source(ip="localhost", port=port_allocator())

    network_destination = config.create_network_destination(
        ip="localhost",
        port=port_allocator(),
        disk_buffer={
            "reliable": "no",
            "dir": "'.'",
            "capacity-bytes": option_capacity_bytes,
            "front-cache-size": option_front_cache_size,
        },
    )

    if option_flow_controll:
        config.create_logpath(statements=[network_source, network_destination], flags="flow-control")
    else:
        config.create_logpath(statements=[network_source, network_destination])
    syslog_ng.start(config)

    counter = 10000
    loggen.start(
        LoggenStartParams(
            target=network_source.options["ip"],
            port=network_source.options["port"],
            inet=True,
            stream=True,
            number=counter,
        ),
    )
    wait_until_true(lambda: loggen.get_sent_message_count() == counter)
    syslog_ng.stop()

# def test_non_reliable_disk_buffer_file_creation_with_default_settings():
#     pass

# def test_non_reliable_disk_buffer_file_creation_with_custom_settings():
#     pass

# def test_non_reliable_disk_buffer_stats_with_default_settings():
#     pass

# def test_non_reliable_disk_buffer_stats_with_custom_settings():
#     pass

# def test_non_reliable_disk_buffer_fill_diskbuffer_until_full_without_flow_control():
#     pass

# def test_non_reliable_disk_buffer_fill_diskbuffer_until_full_without_flow_control():
#     pass

# def test_non_reliable_disk_buffer_network_destination(config, syslog_ng, syslog_ng_ctl, port_allocator, loggen):
#     counter = 2000
#     message = "TEST MESSAGE "*20

#     config.update_global_options(stats_level=5)
#     network_source = config.create_network_source(ip="localhost", port=port_allocator())

#     network_destination = config.create_network_destination(
#         ip="localhost",
#         port=port_allocator(),
#         disk_buffer={
#             "reliable": "no",
#             "dir": "'.'",
#             "capacity-bytes": "1Mib",
#             "front-cache-size": "500",
#         },
#     )

#     config.create_logpath(statements=[network_source, network_destination])
#     syslog_ng.start(config)
#     loggen.start(
#         LoggenStartParams(
#             target=network_source.options["ip"],
#             port=network_source.options["port"],
#             inet=True,
#             stream=True,
#             number=counter,
#         ),
#     )
#     wait_until_true(lambda: loggen.get_sent_message_count() == counter)

#     print(syslog_ng_ctl.stats_prometheus())

#     # network_destination.start_listener()
#     # assert network_destination.read_until_logs([test_message])

# -------------------------
# def test_non_reliable_disk_buffer_default_settings_without_flow_control():
#     # jobb teszt nev: test_non_reliable_disk_buffer_fill_diskbuffer_until_full_without_flow_control
#     # default disk-buffer settings
#         # modules/diskq/diskq-options.h
#         # 30:#define MIN_CAPACITY_BYTES 1024*1024

#     # flow-control is disabled
#     # destination is unreachable
#     # messages should be dropped when buffer is full
#     # start destination
#     # messages from disk-buffer should be sent to destination
#     # new messages should be arrived to destination too
#     # message loss is acceptable
#     # no message duplication should happen
#     # check ctl-stats
#     # check ctl prometheus metrics

# def test_non_reliable_disk_buffer_default_settings_with_flow_control():
#     # default disk-buffer settings
#     # flow-control is disabled
#     # destination is unreachable
#     # source should be blocked when buffer is full
#     # start destination
#     # messages from disk-buffer should be sent to destination
#     # new messages should be arrived to destination too
#     # message loss is not acceptable
#     # no message duplication should happen
#     # check ctl-stats
#     # check ctl prometheus metrics
