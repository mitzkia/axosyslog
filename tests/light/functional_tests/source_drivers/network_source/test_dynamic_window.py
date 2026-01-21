#!/usr/bin/env python
#############################################################################
# Copyright (c) 2026 Axoflow
# Copyright (c) 2026 Andras Mitzki <andras.mitzki@axoflow.com>
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
# import time
import pytest
from axosyslog_light.common.blocking import wait_until_true
from axosyslog_light.helpers.loggen.loggen import LoggenStartParams

NUMBER_OF_MESSAGES = 100000

# mikor mennyi uzenetet lehet bekuldeni ha a dst nem el
# menet kozben mehetnek a reload-ok
# menet kozben megprobalhatjuk ki-be kapcsolni a dst-t
# mi van ha tobb source is hasznalja a dynamic window-t egyszerre
# loggen: active connections = 1 -tol 20-ig + number 1000 - 20000+ ig
# menet kozben nezzunk stats-okat
# flow-control be/ki
# source keep_alive be/ki
# 1,  max_connections = 20, log_iw_size = 10000, log_fetch_limit = 1000
# 2,  max_connections = 20, log_iw_size = 10000, log_fetch_limit = 1000, dynamic_window_size = 0
# 3,  max_connections = 20, log_iw_size = 10000, log_fetch_limit = 1000, dynamic_window_size = 10
# 4,  max_connections = 20, log_iw_size = 10000, log_fetch_limit = 1000, dynamic_window_size = 1000
# 5,  max_connections = 20, log_iw_size = 10000, log_fetch_limit = 1000, dynamic_window_size = 20000
# a lenti msg_trace() es msg_info() logokat kikenyszeriteni

# def test_dynamic_window(config, syslog_ng, port_allocator, loggen, syslog_ng_ctl):
#     server_port = port_allocator()
#     config.update_global_options(stats_level=5)
#     network_source = config.create_network_source(ip="localhost", port=server_port, log_iw_size=100000, dynamic_window_size=100000, dynamic_window_stats_freq=1, dynamic_window_realloc_ticks=10, max_connections=100, keep_alive=True)

#     file_destination = config.create_file_destination(file_name="output.txt")
#     config.create_logpath(statements=[network_source, file_destination])

#     syslog_ng.start(config)


#     loggen.start(
#         LoggenStartParams(
#             target=network_source.options["ip"],
#             port=network_source.options["port"],
#             inet=True,
#             rate=100000,
#             active_connections=5,
#             reconnect=True,
#             interval=5,
#             number=NUMBER_OF_MESSAGES,
#         ),
#     )
#     wait_until_true(lambda: loggen.get_sent_message_count() == 5 * NUMBER_OF_MESSAGES)
#     print(syslog_ng_ctl.stats())
#     print(syslog_ng_ctl.stats_prometheus())

#     import time
#     time.sleep(5)
#     print(syslog_ng_ctl.stats())
#     print(syslog_ng_ctl.stats_prometheus())

# 1,  max_connections = 20, log_iw_size = 10000, log_fetch_limit = 1000
# 2,  max_connections = 20, log_iw_size = 10000, log_fetch_limit = 1000, dynamic_window_size = 0
# 3,  max_connections = 20, log_iw_size = 10000, log_fetch_limit = 1000, dynamic_window_size = 10
# 4,  max_connections = 20, log_iw_size = 10000, log_fetch_limit = 1000, dynamic_window_size = 1000
# 5,  max_connections = 20, log_iw_size = 10000, log_fetch_limit = 1000, dynamic_window_size = 20000


@pytest.mark.parametrize(
    "log_iw_size, log_fetch_limit, dynamic_window_size, loggen_msg_counter", [
        # (10000, 1000, None),
        # (10000, 1000, 0, 1100),
        # (10000, 1000, 10, 1100),
        # (10000, 1000, 1000, 3000),
        (10000, 1000, 2000, 3000),
    ],
)
def test_dynamic_window_placeholder(config, syslog_ng, port_allocator, loggen, syslog_ng_ctl, log_iw_size, log_fetch_limit, dynamic_window_size, loggen_msg_counter):
    config.update_global_options(stats_level=5)
    network_source = config.create_network_source(
        ip="localhost",
        port=port_allocator(),
        log_iw_size=log_iw_size,
        log_fetch_limit=log_fetch_limit,
        dynamic_window_size=dynamic_window_size,
        # dynamic_window_stats_freq=1,
        dynamic_window_realloc_ticks=3,
        max_connections=10,
        keep_alive="yes",
    )
    network_destination = config.create_network_destination(ip="localhost", port=port_allocator())
    config.create_logpath(statements=[network_source, network_destination], flags="flow-control")
    syslog_ng.start(config)
    loggen.start(
        LoggenStartParams(
            target=network_source.options["ip"],
            port=network_source.options["port"],
            inet=True,
            rate=10000,
            active_connections=1,
            number=loggen_msg_counter,
        ),
    )
    wait_until_true(lambda: loggen.get_sent_message_count() == loggen_msg_counter)
    messages_to_processed_first = 1000  # log_iw_size
    assert network_source.get_stats()["processed"] == messages_to_processed_first
    assert network_destination.get_stats()["processed"] == messages_to_processed_first
    assert network_destination.get_stats()["queued"] == messages_to_processed_first

    assert wait_until_true(lambda: "processed" in network_source.get_stats() and network_source.get_stats()["processed"] == loggen_msg_counter)
    assert network_destination.get_stats()["processed"] == loggen_msg_counter
    assert network_destination.get_stats()["queued"] == loggen_msg_counter

    syslog_ng.stop()
    assert syslog_ng.are_messages_in_console_log([
        "Source has been suspended",
        "Dynamic window timer elapsed; tick='1'",
        "Dynamic window timer elapsed; tick='2'",
        "Dynamic window timer elapsed; tick='3'",
        "LogReader::dynamic_window_realloc called",
        "Checking if reclaim is in progress...;",
        "full_window='1000', dynamic_win='0', static_window='1000', balanced_window='2000', avg_free='0'",
        "old_full_window_size='1000', new_full_window_size='3000'",
    ])
    assert not syslog_ng.is_message_in_console_log("Dynamic window timer elapsed; tick='4'")


# log {
#   source {
#     network(port(4444) log-iw-size(4000) max-connections(10) dynamic-window-size(100000) keep-alive(yes));
#   };
# };

# micek@micek-ThinkPad-T14-Gen-4:~/source/axosyslog/lib$ rg -i "dynamic window"
# logsource.c
# 215:  msg_trace("Updating dynamic window statistic", evt_tag_int("avg window size",
# 341:  msg_trace("Rebalance dynamic window",

# tests/test_logsource.c
# 393:            "Source should not be suspended as it should own free dynamic window slots");
# micek@micek-ThinkPad-T14-Gen-4:~/source/axosyslog/lib$ cd ../modules/
# micek@micek-ThinkPad-T14-Gen-4:~/source/axosyslog/modules$ rg -i "dynamic window"
# afsocket/afsocket-source.c
# 631:      msg_info("Cannot allocate more dynamic window for new clients. From now, only static window is allocated."
# 669:  msg_trace("Dynamic window timer elapsed", evt_tag_int("tick", self->dynamic_window_timer_tick));

# [2026-01-20T11:22:45.589408] Updating dynamic window statistic; avg window size='4'
# [2026-01-20T11:22:45.589408] Updating dynamic window statistic; avg window size='7'
# [2026-01-20T11:22:45.589408] Updating dynamic window statistic; avg window size='7'
# [2026-01-20T11:22:45.589408] Updating dynamic window statistic; avg window size='9'
# [2026-01-20T11:22:45.589408] Updating dynamic window statistic; avg window size='6'
# [2026-01-20T11:22:45.589408] Dynamic window timer elapsed; tick='1'
# [2026-01-20T11:22:46.589425] Updating dynamic window statistic; avg window size='5'
# [2026-01-20T11:22:46.589425] Updating dynamic window statistic; avg window size='8'
# [2026-01-20T11:22:46.589425] Updating dynamic window statistic; avg window size='6'
# [2026-01-20T11:22:46.589425] Updating dynamic window statistic; avg window size='8'
# [2026-01-20T11:22:46.589425] Updating dynamic window statistic; avg window size='8'
# [2026-01-20T11:22:46.589425] Dynamic window timer elapsed; tick='2'
# [2026-01-20T11:22:47.589435] Updating dynamic window statistic; avg window size='5'
# [2026-01-20T11:22:47.589435] Updating dynamic window statistic; avg window size='5'
# [2026-01-20T11:22:47.589435] Updating dynamic window statistic; avg window size='7'
# [2026-01-20T11:22:47.589435] Updating dynamic window statistic; avg window size='8'
# [2026-01-20T11:22:47.589435] Updating dynamic window statistic; avg window size='7'
# [2026-01-20T11:22:47.589435] Dynamic window timer elapsed; tick='3'
# [2026-01-20T11:22:48.589449] Updating dynamic window statistic; avg window size='4'
# [2026-01-20T11:22:48.589449] Updating dynamic window statistic; avg window size='5'
# [2026-01-20T11:22:48.589449] Updating dynamic window statistic; avg window size='5'
# [2026-01-20T11:22:48.589449] Updating dynamic window statistic; avg window size='7'
# [2026-01-20T11:22:48.589449] Updating dynamic window statistic; avg window size='5'
# [2026-01-20T11:22:48.589449] Dynamic window timer elapsed; tick='4'
# [2026-01-20T11:22:49.589459] Updating dynamic window statistic; avg window size='5'
# [2026-01-20T11:22:49.589459] Updating dynamic window statistic; avg window size='4'
# [2026-01-20T11:22:49.589459] Updating dynamic window statistic; avg window size='5'
# [2026-01-20T11:22:49.589459] Updating dynamic window statistic; avg window size='6'
# [2026-01-20T11:22:49.589459] Updating dynamic window statistic; avg window size='5'
# [2026-01-20T11:22:49.589459] Dynamic window timer elapsed; tick='5'
# [2026-01-20T11:22:50.589469] Updating dynamic window statistic; avg window size='6'
# [2026-01-20T11:22:50.589469] Updating dynamic window statistic; avg window size='5'
# [2026-01-20T11:22:50.589469] Updating dynamic window statistic; avg window size='6'
# [2026-01-20T11:22:50.589469] Updating dynamic window statistic; avg window size='7'
# [2026-01-20T11:22:50.589469] Updating dynamic window statistic; avg window size='4'
# [2026-01-20T11:22:50.589469] Dynamic window timer elapsed; tick='6'
# [2026-01-20T11:22:51.589488] Updating dynamic window statistic; avg window size='6'
# [2026-01-20T11:22:51.589488] Updating dynamic window statistic; avg window size='4'
# [2026-01-20T11:22:51.589488] Updating dynamic window statistic; avg window size='5'
# [2026-01-20T11:22:51.589488] Updating dynamic window statistic; avg window size='6'
# [2026-01-20T11:22:51.589488] Updating dynamic window statistic; avg window size='3'
# [2026-01-20T11:22:51.589488] Dynamic window timer elapsed; tick='7'
# [2026-01-20T11:22:52.589504] Updating dynamic window statistic; avg window size='6'
# [2026-01-20T11:22:52.589504] Updating dynamic window statistic; avg window size='4'
# [2026-01-20T11:22:52.589504] Updating dynamic window statistic; avg window size='5'
# [2026-01-20T11:22:52.589504] Updating dynamic window statistic; avg window size='5'
# [2026-01-20T11:22:52.589504] Updating dynamic window statistic; avg window size='3'
# [2026-01-20T11:22:52.589504] Dynamic window timer elapsed; tick='8'
# [2026-01-20T11:22:53.589526] Updating dynamic window statistic; avg window size='6'
# [2026-01-20T11:22:53.589526] Updating dynamic window statistic; avg window size='3'
# [2026-01-20T11:22:53.589526] Updating dynamic window statistic; avg window size='5'
# [2026-01-20T11:22:53.589526] Updating dynamic window statistic; avg window size='5'
# [2026-01-20T11:22:53.589526] Updating dynamic window statistic; avg window size='3'
# [2026-01-20T11:22:53.589526] Dynamic window timer elapsed; tick='9'
# [2026-01-20T11:22:54.589533] Updating dynamic window statistic; avg window size='5'
# [2026-01-20T11:22:54.589533] Updating dynamic window statistic; avg window size='4'
# [2026-01-20T11:22:54.589533] Updating dynamic window statistic; avg window size='4'
# [2026-01-20T11:22:54.589533] Updating dynamic window statistic; avg window size='5'
# [2026-01-20T11:22:54.589533] Updating dynamic window statistic; avg window size='3'
# [2026-01-20T11:22:54.589533] Dynamic window timer elapsed; tick='10'
# [2026-01-20T11:22:55.589551] LogReader::dynamic_window_realloc called;
# [2026-01-20T11:22:55.589551] LogReader::dynamic_window_realloc called;
# [2026-01-20T11:22:55.589551] Rebalance dynamic window; location='syslog_ng_server.conf:7:5', connection='0x5d7b968d2220', full_window='10', dynamic_win='0', static_window='10', balanced_window='20000', avg_free='4'
# [2026-01-20T11:22:55.589551] LogReader::dynamic_window_realloc called;
# [2026-01-20T11:22:55.589551] LogReader::dynamic_window_realloc called;
# [2026-01-20T11:22:55.589551] LogReader::dynamic_window_realloc called;
# [2026-01-20T11:22:55.589551] Dynamic window timer elapsed; tick='1'
# [2026-01-20T11:22:55.592731] Rebalance dynamic window; location='syslog_ng_server.conf:7:5', connection='0x5d7b968d4430', full_window='10', dynamic_win='0', static_window='10', balanced_window='20000', avg_free='5'
# [2026-01-20T11:22:55.592931] Rebalance dynamic window; location='syslog_ng_server.conf:7:5', connection='0x5d7b968d0010', full_window='10', dynamic_win='0', static_window='10', balanced_window='20000', avg_free='4'
# [2026-01-20T11:22:55.594897] Rebalance dynamic window; location='syslog_ng_server.conf:7:5', connection='0x5d7b968cdd40', full_window='10', dynamic_win='0', static_window='10', balanced_window='20000', avg_free='5'
# [2026-01-20T11:22:55.595684] Rebalance dynamic window; location='syslog_ng_server.conf:7:5', connection='0x5d7b96848680', full_window='10', dynamic_win='0', static_window='10', balanced_window='20000', avg_free='3'
# [2026-01-20T11:22:56.589559] Updating dynamic window statistic; avg window size='20001'
# [2026-01-20T11:22:56.589559] Updating dynamic window statistic; avg window size='20006'
# [2026-01-20T11:22:56.589559] Updating dynamic window statistic; avg window size='20000'
# [2026-01-20T11:22:56.589559] Updating dynamic window statistic; avg window size='20006'
# [2026-01-20T11:22:56.589559] Updating dynamic window statistic; avg window size='19999'
# [2026-01-20T11:22:56.589559] Dynamic window timer elapsed; tick='2'
# [2026-01-20T11:22:57.589567] Updating dynamic window statistic; avg window size='20004'
# [2026-01-20T11:22:57.589567] Updating dynamic window statistic; avg window size='20003'
# [2026-01-20T11:22:57.589567] Updating dynamic window statistic; avg window size='20003'
# [2026-01-20T11:22:57.589567] Updating dynamic window statistic; avg window size='20005'
# [2026-01-20T11:22:57.589567] Updating dynamic window statistic; avg window size='20003'
# [2026-01-20T11:22:57.589567] Dynamic window timer elapsed; tick='3'
# [2026-01-20T11:22:58.589583] Updating dynamic window statistic; avg window size='20003'
# [2026-01-20T11:22:58.589583] Updating dynamic window statistic; avg window size='20002'
# [2026-01-20T11:22:58.589583] Updating dynamic window statistic; avg window size='20005'
# [2026-01-20T11:22:58.589583] Updating dynamic window statistic; avg window size='20006'
# [2026-01-20T11:22:58.589583] Updating dynamic window statistic; avg window size='20004'
# [2026-01-20T11:22:58.589583] Dynamic window timer elapsed; tick='4'
# [2026-01-20T11:22:59.589589] Updating dynamic window statistic; avg window size='20004'
# [2026-01-20T11:22:59.589589] Updating dynamic window statistic; avg window size='20003'
# [2026-01-20T11:22:59.589589] Updating dynamic window statistic; avg window size='20003'
# [2026-01-20T11:22:59.589589] Updating dynamic window statistic; avg window size='20006'
# [2026-01-20T11:22:59.589589] Updating dynamic window statistic; avg window size='20003'
# [2026-01-20T11:22:59.589589] Dynamic window timer elapsed; tick='5'
# [2026-01-20T11:23:00.589601] Updating dynamic window statistic; avg window size='20004'
# [2026-01-20T11:23:00.589601] Updating dynamic window statistic; avg window size='20004'
# [2026-01-20T11:23:00.589601] Updating dynamic window statistic; avg window size='20004'
# [2026-01-20T11:23:00.589601] Updating dynamic window statistic; avg window size='20005'
# [2026-01-20T11:23:00.589601] Updating dynamic window statistic; avg window size='20003'
# [2026-01-20T11:23:00.589601] Dynamic window timer elapsed; tick='6'
# [2026-01-20T11:23:01.589610] Updating dynamic window statistic; avg window size='20004'
# [2026-01-20T11:23:01.589610] Updating dynamic window statistic; avg window size='20003'
# [2026-01-20T11:23:01.589610] Updating dynamic window statistic; avg window size='20004'
# [2026-01-20T11:23:01.589610] Updating dynamic window statistic; avg window size='20004'
# [2026-01-20T11:23:01.589610] Updating dynamic window statistic; avg window size='20002'
# [2026-01-20T11:23:01.589610] Dynamic window timer elapsed; tick='7'
# [2026-01-20T11:23:02.589620] Updating dynamic window statistic; avg window size='20004'
# [2026-01-20T11:23:02.589620] Updating dynamic window statistic; avg window size='20004'
# [2026-01-20T11:23:02.589620] Updating dynamic window statistic; avg window size='20004'
# [2026-01-20T11:23:02.589620] Updating dynamic window statistic; avg window size='20005'
# [2026-01-20T11:23:02.589620] Updating dynamic window statistic; avg window size='20003'
# [2026-01-20T11:23:02.589620] Dynamic window timer elapsed; tick='8'
# [2026-01-20T11:23:03.589633] Updating dynamic window statistic; avg window size='20003'
# [2026-01-20T11:23:03.589633] Updating dynamic window statistic; avg window size='20004'
# [2026-01-20T11:23:03.589633] Updating dynamic window statistic; avg window size='20004'
# [2026-01-20T11:23:03.589633] Updating dynamic window statistic; avg window size='20005'
# [2026-01-20T11:23:03.589633] Updating dynamic window statistic; avg window size='20003'
# [2026-01-20T11:23:03.589633] Dynamic window timer elapsed; tick='9'
# [2026-01-20T11:23:04.589651] Updating dynamic window statistic; avg window size='20004'
# [2026-01-20T11:23:04.589651] Updating dynamic window statistic; avg window size='20004'
# [2026-01-20T11:23:04.589651] Updating dynamic window statistic; avg window size='20004'
# [2026-01-20T11:23:04.589651] Updating dynamic window statistic; avg window size='20004'
# [2026-01-20T11:23:04.589651] Updating dynamic window statistic; avg window size='20003'
# [2026-01-20T11:23:04.589651] Dynamic window timer elapsed; tick='10'
# [2026-01-20T11:23:05.589659] LogReader::dynamic_window_realloc called;
# [2026-01-20T11:23:05.589659] LogReader::dynamic_window_realloc called;
# [2026-01-20T11:23:05.589659] LogReader::dynamic_window_realloc called;
# [2026-01-20T11:23:05.589659] LogReader::dynamic_window_realloc called;
# [2026-01-20T11:23:05.589659] LogReader::dynamic_window_realloc called;
# [2026-01-20T11:23:05.589659] Dynamic window timer elapsed; tick='1'
# [2026-01-20T11:23:05.590593] Rebalance dynamic window; location='syslog_ng_server.conf:7:5', connection='0x5d7b968d0010', full_window='20010', dynamic_win='20000', static_window='10', balanced_window='20000', avg_free='20004'
# [2026-01-20T11:23:05.591307] Rebalance dynamic window; location='syslog_ng_server.conf:7:5', connection='0x5d7b968d2220', full_window='20010', dynamic_win='20000', static_window='10', balanced_window='20000', avg_free='20004'
# [2026-01-20T11:23:05.592817] Rebalance dynamic window; location='syslog_ng_server.conf:7:5', connection='0x5d7b968cdd40', full_window='20010', dynamic_win='20000', static_window='10', balanced_window='20000', avg_free='20004'
# [2026-01-20T11:23:05.594681] Rebalance dynamic window; location='syslog_ng_server.conf:7:5', connection='0x5d7b96848680', full_window='20010', dynamic_win='20000', static_window='10', balanced_window='20000', avg_free='20003'
# [2026-01-20T11:23:05.594768] Rebalance dynamic window; location='syslog_ng_server.conf:7:5', connection='0x5d7b968d4430', full_window='20010', dynamic_win='20000', static_window='10', balanced_window='20000', avg_free='20004'
# [2026-01-20T11:23:06.589672] Updating dynamic window statistic; avg window size='20004'
# [2026-01-20T11:23:06.589672] Updating dynamic window statistic; avg window size='20004'
# [2026-01-20T11:23:06.589672] Updating dynamic window statistic; avg window size='20000'
# [2026-01-20T11:23:06.589672] Updating dynamic window statistic; avg window size='20001'
# [2026-01-20T11:23:06.589672] Updating dynamic window statistic; avg window size='20005'
# [2026-01-20T11:23:06.589672] Dynamic window timer elapsed; tick='2'
# [2026-01-20T11:23:07.589676] Updating dynamic window statistic; avg window size='20004'
# [2026-01-20T11:23:07.589676] Updating dynamic window statistic; avg window size='20002'
# [2026-01-20T11:23:07.589676] Updating dynamic window statistic; avg window size='20001'
# [2026-01-20T11:23:07.589676] Updating dynamic window statistic; avg window size='20001'
# [2026-01-20T11:23:07.589676] Updating dynamic window statistic; avg window size='20004'
# [2026-01-20T11:23:07.589676] Dynamic window timer elapsed; tick='3'
# [2026-01-20T11:23:08.589687] Updating dynamic window statistic; avg window size='20002'
# [2026-01-20T11:23:08.589687] Updating dynamic window statistic; avg window size='20000'
# [2026-01-20T11:23:08.589687] Updating dynamic window statistic; avg window size='20000'
# [2026-01-20T11:23:08.589687] Updating dynamic window statistic; avg window size='19999'
# [2026-01-20T11:23:08.589687] Updating dynamic window statistic; avg window size='20004'
# [2026-01-20T11:23:08.589687] Dynamic window timer elapsed; tick='4'
# [2026-01-20T11:23:09.589698] Updating dynamic window statistic; avg window size='20002'
# [2026-01-20T11:23:09.589698] Updating dynamic window statistic; avg window size='20002'
# [2026-01-20T11:23:09.589698] Updating dynamic window statistic; avg window size='20002'
# [2026-01-20T11:23:09.589698] Updating dynamic window statistic; avg window size='20001'
# [2026-01-20T11:23:09.589698] Updating dynamic window statistic; avg window size='20003'
# [2026-01-20T11:23:09.589698] Dynamic window timer elapsed; tick='5'
# [2026-01-20T11:23:10.589706] Updating dynamic window statistic; avg window size='20003'
# [2026-01-20T11:23:10.589706] Updating dynamic window statistic; avg window size='20003'
# [2026-01-20T11:23:10.589706] Updating dynamic window statistic; avg window size='20003'
# [2026-01-20T11:23:10.589706] Updating dynamic window statistic; avg window size='20001'
# [2026-01-20T11:23:10.589706] Updating dynamic window statistic; avg window size='20003'
# [2026-01-20T11:23:10.589706] Dynamic window timer elapsed; tick='6'
# [2026-01-20T11:23:11.589713] Updating dynamic window statistic; avg window size='20004'
# [2026-01-20T11:23:11.589713] Updating dynamic window statistic; avg window size='20003'
# [2026-01-20T11:23:11.589713] Updating dynamic window statistic; avg window size='20002'
# [2026-01-20T11:23:11.589713] Updating dynamic window statistic; avg window size='20002'
# [2026-01-20T11:23:11.589713] Updating dynamic window statistic; avg window size='20004'
# [2026-01-20T11:23:11.589713] Dynamic window timer elapsed; tick='7'
# [2026-01-20T11:23:12.589724] Updating dynamic window statistic; avg window size='20004'
# [2026-01-20T11:23:12.589724] Updating dynamic window statistic; avg window size='20003'
# [2026-01-20T11:23:12.589724] Updating dynamic window statistic; avg window size='20003'
# [2026-01-20T11:23:12.589724] Updating dynamic window statistic; avg window size='20003'
# [2026-01-20T11:23:12.589724] Updating dynamic window statistic; avg window size='20004'
# [2026-01-20T11:23:12.589724] Dynamic window timer elapsed; tick='8'
# [2026-01-20T11:23:13.589739] Updating dynamic window statistic; avg window size='20003'
# [2026-01-20T11:23:13.589739] Updating dynamic window statistic; avg window size='20001'
# [2026-01-20T11:23:13.589739] Updating dynamic window statistic; avg window size='20002'
# [2026-01-20T11:23:13.589739] Updating dynamic window statistic; avg window size='20002'
# [2026-01-20T11:23:13.589739] Updating dynamic window statistic; avg window size='20003'
# [2026-01-20T11:23:13.589739] Dynamic window timer elapsed; tick='9'
# [2026-01-20T11:23:14.589748] Updating dynamic window statistic; avg window size='20002'
# [2026-01-20T11:23:14.589748] Updating dynamic window statistic; avg window size='20001'
# [2026-01-20T11:23:14.589748] Updating dynamic window statistic; avg window size='20003'
# [2026-01-20T11:23:14.589748] Updating dynamic window statistic; avg window size='20002'
# [2026-01-20T11:23:14.589748] Updating dynamic window statistic; avg window size='20002'
# [2026-01-20T11:23:14.589748] Dynamic window timer elapsed; tick='10'
# [2026-01-20T11:23:15.589753] LogReader::dynamic_window_realloc called;
# [2026-01-20T11:23:15.589753] LogReader::dynamic_window_realloc called;
# [2026-01-20T11:23:15.589753] LogReader::dynamic_window_realloc called;
# [2026-01-20T11:23:15.589753] LogReader::dynamic_window_realloc called;
# [2026-01-20T11:23:15.589753] LogReader::dynamic_window_realloc called;
# [2026-01-20T11:23:15.589753] Dynamic window timer elapsed; tick='1'
# [2026-01-20T11:23:15.592202] Rebalance dynamic window; location='syslog_ng_server.conf:7:5', connection='0x5d7b968d4430', full_window='20010', dynamic_win='20000', static_window='10', balanced_window='20000', avg_free='20002'
# [2026-01-20T11:23:15.593832] Rebalance dynamic window; location='syslog_ng_server.conf:7:5', connection='0x5d7b96848680', full_window='20010', dynamic_win='20000', static_window='10', balanced_window='20000', avg_free='20002'
# [2026-01-20T11:23:15.595474] Rebalance dynamic window; location='syslog_ng_server.conf:7:5', connection='0x5d7b968d2220', full_window='20010', dynamic_win='20000', static_window='10', balanced_window='20000', avg_free='20001'
# [2026-01-20T11:23:15.595560] Rebalance dynamic window; location='syslog_ng_server.conf:7:5', connection='0x5d7b968cdd40', full_window='20010', dynamic_win='20000', static_window='10', balanced_window='20000', avg_free='20002'
# [2026-01-20T11:23:15.595735] Rebalance dynamic window; location='syslog_ng_server.conf:7:5', connection='0x5d7b968d0010', full_window='20010', dynamic_win='20000', static_window='10', balanced_window='20000', avg_free='20003'
# [2026-01-20T11:23:16.589773] Updating dynamic window statistic; avg window size='19998'
# [2026-01-20T11:23:16.589773] Updating dynamic window statistic; avg window size='20004'
# [2026-01-20T11:23:16.589773] Updating dynamic window statistic; avg window size='20006'
# [2026-01-20T11:23:16.589773] Updating dynamic window statistic; avg window size='20001'
# [2026-01-20T11:23:16.589773] Updating dynamic window statistic; avg window size='20000'
# [2026-01-20T11:23:16.589773] Dynamic window timer elapsed; tick='2'
# [2026-01-20T11:23:17.589780] Updating dynamic window statistic; avg window size='19999'
# [2026-01-20T11:23:17.589780] Updating dynamic window statistic; avg window size='20005'
# [2026-01-20T11:23:17.589780] Updating dynamic window statistic; avg window size='20005'
# [2026-01-20T11:23:17.589780] Updating dynamic window statistic; avg window size='20004'
# [2026-01-20T11:23:17.589780] Updating dynamic window statistic; avg window size='20002'
# [2026-01-20T11:23:17.589780] Dynamic window timer elapsed; tick='3'
# [2026-01-20T11:23:18.589788] Updating dynamic window statistic; avg window size='19999'
# [2026-01-20T11:23:18.589788] Updating dynamic window statistic; avg window size='20004'
# [2026-01-20T11:23:18.589788] Updating dynamic window statistic; avg window size='20004'
# [2026-01-20T11:23:18.589788] Updating dynamic window statistic; avg window size='20003'
# [2026-01-20T11:23:18.589788] Updating dynamic window statistic; avg window size='20001'
# [2026-01-20T11:23:18.589788] Dynamic window timer elapsed; tick='4'
# [2026-01-20T11:23:19.589801] Updating dynamic window statistic; avg window size='20000'
# [2026-01-20T11:23:19.589801] Updating dynamic window statistic; avg window size='20005'
# [2026-01-20T11:23:19.589801] Updating dynamic window statistic; avg window size='20004'
# [2026-01-20T11:23:19.589801] Updating dynamic window statistic; avg window size='20003'
# [2026-01-20T11:23:19.589801] Updating dynamic window statistic; avg window size='20002'
# [2026-01-20T11:23:19.589801] Dynamic window timer elapsed; tick='5'
# [2026-01-20T11:23:20.589809] Updating dynamic window statistic; avg window size='20000'
# [2026-01-20T11:23:20.589809] Updating dynamic window statistic; avg window size='20004'
# [2026-01-20T11:23:20.589809] Updating dynamic window statistic; avg window size='20004'
# [2026-01-20T11:23:20.589809] Updating dynamic window statistic; avg window size='20002'
# [2026-01-20T11:23:20.589809] Updating dynamic window statistic; avg window size='20002'
# [2026-01-20T11:23:20.589809] Dynamic window timer elapsed; tick='6'
# [2026-01-20T11:23:21.589820] Updating dynamic window statistic; avg window size='20000'
# [2026-01-20T11:23:21.589820] Updating dynamic window statistic; avg window size='20003'
# [2026-01-20T11:23:21.589820] Updating dynamic window statistic; avg window size='20004'
# [2026-01-20T11:23:21.589820] Updating dynamic window statistic; avg window size='20003'
# [2026-01-20T11:23:21.589820] Updating dynamic window statistic; avg window size='20002'
# [2026-01-20T11:23:21.589820] Dynamic window timer elapsed; tick='7'
# [2026-01-20T11:23:22.589881] Updating dynamic window statistic; avg window size='20000'
# [2026-01-20T11:23:22.589881] Updating dynamic window statistic; avg window size='20003'
# [2026-01-20T11:23:22.589881] Updating dynamic window statistic; avg window size='20004'
# [2026-01-20T11:23:22.589881] Updating dynamic window statistic; avg window size='20002'
# [2026-01-20T11:23:22.589881] Updating dynamic window statistic; avg window size='20001'
# [2026-01-20T11:23:22.589881] Dynamic window timer elapsed; tick='8'
# [2026-01-20T11:23:23.589898] Updating dynamic window statistic; avg window size='20000'
# [2026-01-20T11:23:23.589898] Updating dynamic window statistic; avg window size='20003'
# [2026-01-20T11:23:23.589898] Updating dynamic window statistic; avg window size='20004'
# [2026-01-20T11:23:23.589898] Updating dynamic window statistic; avg window size='20002'
# [2026-01-20T11:23:23.589898] Updating dynamic window statistic; avg window size='20002'
# [2026-01-20T11:23:23.589898] Dynamic window timer elapsed; tick='9'
# [2026-01-20T11:23:24.589904] Updating dynamic window statistic; avg window size='20000'
# [2026-01-20T11:23:24.589904] Updating dynamic window statistic; avg window size='20003'
# [2026-01-20T11:23:24.589904] Updating dynamic window statistic; avg window size='20004'
# [2026-01-20T11:23:24.589904] Updating dynamic window statistic; avg window size='20001'
# [2026-01-20T11:23:24.589904] Updating dynamic window statistic; avg window size='20002'
# [2026-01-20T11:23:24.589904] Dynamic window timer elapsed; tick='10'
# [2026-01-20T11:23:25.589961] LogReader::dynamic_window_realloc called;
# [2026-01-20T11:23:25.589961] Rebalance dynamic window; location='syslog_ng_server.conf:7:5', connection='0x5d7b968d4430', full_window='20010', dynamic_win='20000', static_window='10', balanced_window='20000', avg_free='20000'
# [2026-01-20T11:23:25.589961] LogReader::dynamic_window_realloc called;
# [2026-01-20T11:23:25.589961] Rebalance dynamic window; location='syslog_ng_server.conf:7:5', connection='0x5d7b968d2220', full_window='20010', dynamic_win='20000', static_window='10', balanced_window='20000', avg_free='20003'
# [2026-01-20T11:23:25.589961] LogReader::dynamic_window_realloc called;
# [2026-01-20T11:23:25.589961] LogReader::dynamic_window_realloc called;
# [2026-01-20T11:23:25.589961] LogReader::dynamic_window_realloc called;
# [2026-01-20T11:23:25.589961] Dynamic window timer elapsed; tick='1'
# [2026-01-20T11:23:25.591014] Rebalance dynamic window; location='syslog_ng_server.conf:7:5', connection='0x5d7b96848680', full_window='20010', dynamic_win='20000', static_window='10', balanced_window='20000', avg_free='20002'
# [2026-01-20T11:23:25.594885] Rebalance dynamic window; location='syslog_ng_server.conf:7:5', connection='0x5d7b968d0010', full_window='20010', dynamic_win='20000', static_window='10', balanced_window='20000', avg_free='20004'
# [2026-01-20T11:23:25.598091] Rebalance dynamic window; location='syslog_ng_server.conf:7:5', connection='0x5d7b968cdd40', full_window='20010', dynamic_win='20000', static_window='10', balanced_window='20000', avg_free='20001'
# [2026-01-20T11:23:26.589975] Updating dynamic window statistic; avg window size='19999'
# [2026-01-20T11:23:26.589975] Updating dynamic window statistic; avg window size='19991'
# [2026-01-20T11:23:26.589975] Updating dynamic window statistic; avg window size='19997'
# [2026-01-20T11:23:26.589975] Updating dynamic window statistic; avg window size='19995'
# [2026-01-20T11:23:26.589975] Updating dynamic window statistic; avg window size='19993'
# [2026-01-20T11:23:26.589975] Dynamic window timer elapsed; tick='2'
# [2026-01-20T11:23:27.589985] Updating dynamic window statistic; avg window size='19999'
# [2026-01-20T11:23:27.589985] Updating dynamic window statistic; avg window size='19997'
# [2026-01-20T11:23:27.589985] Updating dynamic window statistic; avg window size='19999'
# [2026-01-20T11:23:27.589985] Updating dynamic window statistic; avg window size='19995'
# [2026-01-20T11:23:27.589985] Updating dynamic window statistic; avg window size='19999'
# [2026-01-20T11:23:27.589985] Dynamic window timer elapsed; tick='3'
# [2026-01-20T11:23:28.590006] Updating dynamic window statistic; avg window size='19999'
# [2026-01-20T11:23:28.590006] Updating dynamic window statistic; avg window size='19999'
# [2026-01-20T11:23:28.590006] Updating dynamic window statistic; avg window size='19999'
# [2026-01-20T11:23:28.590006] Updating dynamic window statistic; avg window size='19997'
# [2026-01-20T11:23:28.590006] Updating dynamic window statistic; avg window size='20001'
# [2026-01-20T11:23:28.590006] Dynamic window timer elapsed; tick='4'
# [2026-01-20T11:23:29.590011] Updating dynamic window statistic; avg window size='20001'
# [2026-01-20T11:23:29.590011] Updating dynamic window statistic; avg window size='20000'
# [2026-01-20T11:23:29.590011] Updating dynamic window statistic; avg window size='19999'
# [2026-01-20T11:23:29.590011] Updating dynamic window statistic; avg window size='19997'
# [2026-01-20T11:23:29.590011] Updating dynamic window statistic; avg window size='20002'
# [2026-01-20T11:23:29.590011] Dynamic window timer elapsed; tick='5'
# [2026-01-20T11:23:30.590025] Updating dynamic window statistic; avg window size='20000'
# [2026-01-20T11:23:30.590025] Updating dynamic window statistic; avg window size='19999'
# [2026-01-20T11:23:30.590025] Updating dynamic window statistic; avg window size='19999'
# [2026-01-20T11:23:30.590025] Updating dynamic window statistic; avg window size='19996'
# [2026-01-20T11:23:30.590025] Updating dynamic window statistic; avg window size='20002'
# [2026-01-20T11:23:30.590025] Dynamic window timer elapsed; tick='6'
# [2026-01-20T11:23:31.590046] Updating dynamic window statistic; avg window size='20001'
# [2026-01-20T11:23:31.590046] Updating dynamic window statistic; avg window size='20000'
# [2026-01-20T11:23:31.590046] Updating dynamic window statistic; avg window size='20000'
# [2026-01-20T11:23:31.590046] Updating dynamic window statistic; avg window size='19998'
# [2026-01-20T11:23:31.590046] Updating dynamic window statistic; avg window size='20002'
# [2026-01-20T11:23:31.590046] Dynamic window timer elapsed; tick='7'
# [2026-01-20T11:23:32.590055] Updating dynamic window statistic; avg window size='20001'
# [2026-01-20T11:23:32.590055] Updating dynamic window statistic; avg window size='20001'
# [2026-01-20T11:23:32.590055] Updating dynamic window statistic; avg window size='20001'
# [2026-01-20T11:23:32.590055] Updating dynamic window statistic; avg window size='19999'
# [2026-01-20T11:23:32.590055] Updating dynamic window statistic; avg window size='20001'
# [2026-01-20T11:23:32.590055] Dynamic window timer elapsed; tick='8'
# [2026-01-20T11:23:33.590065] Updating dynamic window statistic; avg window size='20002'
# [2026-01-20T11:23:33.590065] Updating dynamic window statistic; avg window size='20001'
# [2026-01-20T11:23:33.590065] Updating dynamic window statistic; avg window size='20001'
# [2026-01-20T11:23:33.590065] Updating dynamic window statistic; avg window size='20000'
# [2026-01-20T11:23:33.590065] Updating dynamic window statistic; avg window size='20001'
# [2026-01-20T11:23:33.590065] Dynamic window timer elapsed; tick='9'
# [2026-01-20T11:23:34.590078] Updating dynamic window statistic; avg window size='20002'
# [2026-01-20T11:23:34.590078] Updating dynamic window statistic; avg window size='20001'
# [2026-01-20T11:23:34.590078] Updating dynamic window statistic; avg window size='20001'
# [2026-01-20T11:23:34.590078] Updating dynamic window statistic; avg window size='20000'
# [2026-01-20T11:23:34.590078] Updating dynamic window statistic; avg window size='20001'
# [2026-01-20T11:23:34.590078] Dynamic window timer elapsed; tick='10'
# [2026-01-20T11:23:35.590097] LogReader::dynamic_window_realloc called;
# [2026-01-20T11:23:35.590097] LogReader::dynamic_window_realloc called;
# [2026-01-20T11:23:35.590097] LogReader::dynamic_window_realloc called;
# [2026-01-20T11:23:35.590097] LogReader::dynamic_window_realloc called;
# [2026-01-20T11:23:35.590097] LogReader::dynamic_window_realloc called;
# [2026-01-20T11:23:35.590097] Dynamic window timer elapsed; tick='1'
# [2026-01-20T11:23:35.592869] Rebalance dynamic window; location='syslog_ng_server.conf:7:5', connection='0x5d7b968d2220', full_window='20010', dynamic_win='20000', static_window='10', balanced_window='20000', avg_free='20001'
# [2026-01-20T11:23:35.593429] Rebalance dynamic window; location='syslog_ng_server.conf:7:5', connection='0x5d7b968d0010', full_window='20010', dynamic_win='20000', static_window='10', balanced_window='20000', avg_free='20001'
# [2026-01-20T11:23:35.593928] Rebalance dynamic window; location='syslog_ng_server.conf:7:5', connection='0x5d7b96848680', full_window='20010', dynamic_win='20000', static_window='10', balanced_window='20000', avg_free='20001'
# [2026-01-20T11:23:35.594833] Rebalance dynamic window; location='syslog_ng_server.conf:7:5', connection='0x5d7b968cdd40', full_window='20010', dynamic_win='20000', static_window='10', balanced_window='20000', avg_free='20000'
# [2026-01-20T11:23:35.595513] Rebalance dynamic window; location='syslog_ng_server.conf:7:5', connection='0x5d7b968d4430', full_window='20010', dynamic_win='20000', static_window='10', balanced_window='20000', avg_free='20002'
# [2026-01-20T11:23:36.590111] Updating dynamic window statistic; avg window size='20004'
# [2026-01-20T11:23:36.590111] Updating dynamic window statistic; avg window size='20000'
# [2026-01-20T11:23:36.590111] Updating dynamic window statistic; avg window size='20004'
# [2026-01-20T11:23:36.590111] Updating dynamic window statistic; avg window size='20007'
# [2026-01-20T11:23:36.590111] Updating dynamic window statistic; avg window size='20001'
# [2026-01-20T11:23:36.590111] Dynamic window timer elapsed; tick='2'
# [2026-01-20T11:23:37.590129] Updating dynamic window statistic; avg window size='20005'
# [2026-01-20T11:23:37.590129] Updating dynamic window statistic; avg window size='20000'
# [2026-01-20T11:23:37.590129] Updating dynamic window statistic; avg window size='20005'
# [2026-01-20T11:23:37.590129] Updating dynamic window statistic; avg window size='20006'
# [2026-01-20T11:23:37.590129] Updating dynamic window statistic; avg window size='20004'
# [2026-01-20T11:23:37.590129] Dynamic window timer elapsed; tick='3'
# [2026-01-20T11:23:38.590151] Updating dynamic window statistic; avg window size='20002'
# [2026-01-20T11:23:38.590151] Updating dynamic window statistic; avg window size='20002'
# [2026-01-20T11:23:38.590151] Updating dynamic window statistic; avg window size='20003'
# [2026-01-20T11:23:38.590151] Updating dynamic window statistic; avg window size='20003'
# [2026-01-20T11:23:38.590151] Updating dynamic window statistic; avg window size='20001'
# [2026-01-20T11:23:38.590151] Dynamic window timer elapsed; tick='4'
# [2026-01-20T11:23:39.590165] Updating dynamic window statistic; avg window size='20002'
# [2026-01-20T11:23:39.590165] Updating dynamic window statistic; avg window size='20002'
# [2026-01-20T11:23:39.590165] Updating dynamic window statistic; avg window size='20002'
# [2026-01-20T11:23:39.590165] Updating dynamic window statistic; avg window size='20003'
# [2026-01-20T11:23:39.590165] Updating dynamic window statistic; avg window size='20001'
# [2026-01-20T11:23:39.590165] Dynamic window timer elapsed; tick='5'
# [2026-01-20T11:23:40.590183] Updating dynamic window statistic; avg window size='20002'
# [2026-01-20T11:23:40.590183] Updating dynamic window statistic; avg window size='20003'
# [2026-01-20T11:23:40.590183] Updating dynamic window statistic; avg window size='20003'
# [2026-01-20T11:23:40.590183] Updating dynamic window statistic; avg window size='20002'
# [2026-01-20T11:23:40.590183] Updating dynamic window statistic; avg window size='20002'
# [2026-01-20T11:23:40.590183] Dynamic window timer elapsed; tick='6'
# [2026-01-20T11:23:41.590191] Updating dynamic window statistic; avg window size='20002'
# [2026-01-20T11:23:41.590191] Updating dynamic window statistic; avg window size='20003'
# [2026-01-20T11:23:41.590191] Updating dynamic window statistic; avg window size='20004'
# [2026-01-20T11:23:41.590191] Updating dynamic window statistic; avg window size='20002'
# [2026-01-20T11:23:41.590191] Updating dynamic window statistic; avg window size='20003'
# [2026-01-20T11:23:41.590191] Dynamic window timer elapsed; tick='7'
# [2026-01-20T11:23:42.590206] Updating dynamic window statistic; avg window size='20002'
# [2026-01-20T11:23:42.590206] Updating dynamic window statistic; avg window size='20003'
# [2026-01-20T11:23:42.590206] Updating dynamic window statistic; avg window size='20004'
# [2026-01-20T11:23:42.590206] Updating dynamic window statistic; avg window size='20003'
# [2026-01-20T11:23:42.590206] Updating dynamic window statistic; avg window size='20003'
# [2026-01-20T11:23:42.590206] Dynamic window timer elapsed; tick='8'
# [2026-01-20T11:23:43.590222] Updating dynamic window statistic; avg window size='20002'
# [2026-01-20T11:23:43.590222] Updating dynamic window statistic; avg window size='20003'
# [2026-01-20T11:23:43.590222] Updating dynamic window statistic; avg window size='20003'
# [2026-01-20T11:23:43.590222] Updating dynamic window statistic; avg window size='20002'
# [2026-01-20T11:23:43.590222] Updating dynamic window statistic; avg window size='20003'
# [2026-01-20T11:23:43.590222] Dynamic window timer elapsed; tick='9'
# [2026-01-20T11:23:44.590225] Updating dynamic window statistic; avg window size='20002'
# [2026-01-20T11:23:44.590225] Updating dynamic window statistic; avg window size='20002'
# [2026-01-20T11:23:44.590225] Updating dynamic window statistic; avg window size='20003'
# [2026-01-20T11:23:44.590225] Updating dynamic window statistic; avg window size='20002'
# [2026-01-20T11:23:44.590225] Updating dynamic window statistic; avg window size='20003'
# [2026-01-20T11:23:44.590225] Dynamic window timer elapsed; tick='10'
# [2026-01-20T11:23:45.590234] LogReader::dynamic_window_realloc called;
# [2026-01-20T11:23:45.590234] LogReader::dynamic_window_realloc called;
# [2026-01-20T11:23:45.590234] LogReader::dynamic_window_realloc called;
# [2026-01-20T11:23:45.590234] LogReader::dynamic_window_realloc called;
# [2026-01-20T11:23:45.590234] LogReader::dynamic_window_realloc called;
# [2026-01-20T11:23:45.590234] Dynamic window timer elapsed; tick='1'
# [2026-01-20T11:23:45.591036] Rebalance dynamic window; location='syslog_ng_server.conf:7:5', connection='0x5d7b968d4430', full_window='20010', dynamic_win='20000', static_window='10', balanced_window='20000', avg_free='20002'
# [2026-01-20T11:23:45.591323] Rebalance dynamic window; location='syslog_ng_server.conf:7:5', connection='0x5d7b968d0010', full_window='20010', dynamic_win='20000', static_window='10', balanced_window='20000', avg_free='20003'
# [2026-01-20T11:23:45.592418] Rebalance dynamic window; location='syslog_ng_server.conf:7:5', connection='0x5d7b96848680', full_window='20010', dynamic_win='20000', static_window='10', balanced_window='20000', avg_free='20003'
# [2026-01-20T11:23:45.594066] Rebalance dynamic window; location='syslog_ng_server.conf:7:5', connection='0x5d7b968d2220', full_window='20010', dynamic_win='20000', static_window='10', balanced_window='20000', avg_free='20002'
# [2026-01-20T11:23:45.595728] Rebalance dynamic window; location='syslog_ng_server.conf:7:5', connection='0x5d7b968cdd40', full_window='20010', dynamic_win='20000', static_window='10', balanced_window='20000', avg_free='20002'
# [2026-01-20T11:23:46.590250] Updating dynamic window statistic; avg window size='19997'
# [2026-01-20T11:23:46.590250] Updating dynamic window statistic; avg window size='19998'
# [2026-01-20T11:23:46.590250] Updating dynamic window statistic; avg window size='19998'
# [2026-01-20T11:23:46.590250] Updating dynamic window statistic; avg window size='20000'
# [2026-01-20T11:23:46.590250] Updating dynamic window statistic; avg window size='20005'
# [2026-01-20T11:23:46.590250] Dynamic window timer elapsed; tick='2'
# [2026-01-20T11:23:47.590261] Updating dynamic window statistic; avg window size='19998'
# [2026-01-20T11:23:47.590261] Updating dynamic window statistic; avg window size='20000'
# [2026-01-20T11:23:47.590261] Updating dynamic window statistic; avg window size='19997'
# [2026-01-20T11:23:47.590261] Updating dynamic window statistic; avg window size='19999'
# [2026-01-20T11:23:47.590261] Updating dynamic window statistic; avg window size='20001'
# [2026-01-20T11:23:47.590261] Dynamic window timer elapsed; tick='3'
# [2026-01-20T11:23:48.590268] Updating dynamic window statistic; avg window size='20001'
# [2026-01-20T11:23:48.590268] Updating dynamic window statistic; avg window size='20001'
# [2026-01-20T11:23:48.590268] Updating dynamic window statistic; avg window size='20001'
# [2026-01-20T11:23:48.590268] Updating dynamic window statistic; avg window size='20001'
# [2026-01-20T11:23:48.590268] Updating dynamic window statistic; avg window size='20003'
# [2026-01-20T11:23:48.590268] Dynamic window timer elapsed; tick='4'
# [2026-01-20T11:23:49.590280] Updating dynamic window statistic; avg window size='20002'
# [2026-01-20T11:23:49.590280] Updating dynamic window statistic; avg window size='20001'
# [2026-01-20T11:23:49.590280] Updating dynamic window statistic; avg window size='20002'
# [2026-01-20T11:23:49.590280] Updating dynamic window statistic; avg window size='20002'
# [2026-01-20T11:23:49.590280] Updating dynamic window statistic; avg window size='20004'
# [2026-01-20T11:23:49.590280] Dynamic window timer elapsed; tick='5'
# [2026-01-20T11:23:50.590287] Updating dynamic window statistic; avg window size='20002'
# [2026-01-20T11:23:50.590287] Updating dynamic window statistic; avg window size='20001'
# [2026-01-20T11:23:50.590287] Updating dynamic window statistic; avg window size='20002'
# [2026-01-20T11:23:50.590287] Updating dynamic window statistic; avg window size='20003'
# [2026-01-20T11:23:50.590287] Updating dynamic window statistic; avg window size='20005'
# [2026-01-20T11:23:50.590287] Dynamic window timer elapsed; tick='6'
# [2026-01-20T11:23:51.590296] Updating dynamic window statistic; avg window size='20003'
# [2026-01-20T11:23:51.590296] Updating dynamic window statistic; avg window size='20002'
# [2026-01-20T11:23:51.590296] Updating dynamic window statistic; avg window size='20002'
# [2026-01-20T11:23:51.590296] Updating dynamic window statistic; avg window size='20004'
# [2026-01-20T11:23:51.590296] Updating dynamic window statistic; avg window size='20004'
# [2026-01-20T11:23:51.590296] Dynamic window timer elapsed; tick='7'
# [2026-01-20T11:23:52.590302] Updating dynamic window statistic; avg window size='20004'
# [2026-01-20T11:23:52.590302] Updating dynamic window statistic; avg window size='20003'
# [2026-01-20T11:23:52.590302] Updating dynamic window statistic; avg window size='20002'
# [2026-01-20T11:23:52.590302] Updating dynamic window statistic; avg window size='20004'
# [2026-01-20T11:23:52.590302] Updating dynamic window statistic; avg window size='20003'
# [2026-01-20T11:23:52.590302] Dynamic window timer elapsed; tick='8'
# [2026-01-20T11:23:53.590318] Updating dynamic window statistic; avg window size='20002'
# [2026-01-20T11:23:53.590318] Updating dynamic window statistic; avg window size='20002'
# [2026-01-20T11:23:53.590318] Updating dynamic window statistic; avg window size='20000'
# [2026-01-20T11:23:53.590318] Updating dynamic window statistic; avg window size='20003'
# [2026-01-20T11:23:53.590318] Updating dynamic window statistic; avg window size='20002'
# [2026-01-20T11:23:53.590318] Dynamic window timer elapsed; tick='9'
# [2026-01-20T11:23:54.590333] Updating dynamic window statistic; avg window size='20002'
# [2026-01-20T11:23:54.590333] Updating dynamic window statistic; avg window size='20002'
# [2026-01-20T11:23:54.590333] Updating dynamic window statistic; avg window size='20001'
# [2026-01-20T11:23:54.590333] Updating dynamic window statistic; avg window size='20003'
# [2026-01-20T11:23:54.590333] Updating dynamic window statistic; avg window size='20002'
# [2026-01-20T11:23:54.590333] Dynamic window timer elapsed; tick='10'
# [2026-01-20T11:23:55.590341] LogReader::dynamic_window_realloc called;
# [2026-01-20T11:23:55.590341] LogReader::dynamic_window_realloc called;
# [2026-01-20T11:23:55.590341] LogReader::dynamic_window_realloc called;
# [2026-01-20T11:23:55.590341] LogReader::dynamic_window_realloc called;
# [2026-01-20T11:23:55.590341] LogReader::dynamic_window_realloc called;
# [2026-01-20T11:23:55.590341] Dynamic window timer elapsed; tick='1'
# [2026-01-20T11:23:55.590781] Rebalance dynamic window; location='syslog_ng_server.conf:7:5', connection='0x5d7b968d0010', full_window='20010', dynamic_win='20000', static_window='10', balanced_window='20000', avg_free='20001'
# [2026-01-20T11:23:55.591143] Rebalance dynamic window; location='syslog_ng_server.conf:7:5', connection='0x5d7b968d4430', full_window='20010', dynamic_win='20000', static_window='10', balanced_window='20000', avg_free='20002'
# [2026-01-20T11:23:55.591673] Rebalance dynamic window; location='syslog_ng_server.conf:7:5', connection='0x5d7b96848680', full_window='20010', dynamic_win='20000', static_window='10', balanced_window='20000', avg_free='20002'
# [2026-01-20T11:23:55.591772] Rebalance dynamic window; location='syslog_ng_server.conf:7:5', connection='0x5d7b968cdd40', full_window='20010', dynamic_win='20000', static_window='10', balanced_window='20000', avg_free='20003'
# [2026-01-20T11:23:55.593762] Rebalance dynamic window; location='syslog_ng_server.conf:7:5', connection='0x5d7b968d2220', full_window='20010', dynamic_win='20000', static_window='10', balanced_window='20000', avg_free='20002'
# [2026-01-20T11:23:56.590357] Updating dynamic window statistic; avg window size='20001'
# [2026-01-20T11:23:56.590357] Updating dynamic window statistic; avg window size='20009'
# [2026-01-20T11:23:56.590357] Updating dynamic window statistic; avg window size='20004'
# [2026-01-20T11:23:56.590357] Updating dynamic window statistic; avg window size='20008'
# [2026-01-20T11:23:56.590357] Updating dynamic window statistic; avg window size='20005'
# [2026-01-20T11:23:56.590357] Dynamic window timer elapsed; tick='2'
# [2026-01-20T11:23:57.590365] Updating dynamic window statistic; avg window size='20004'
# [2026-01-20T11:23:57.590365] Updating dynamic window statistic; avg window size='20005'
# [2026-01-20T11:23:57.590365] Updating dynamic window statistic; avg window size='20003'
# [2026-01-20T11:23:57.590365] Updating dynamic window statistic; avg window size='20008'
# [2026-01-20T11:23:57.590365] Updating dynamic window statistic; avg window size='20005'
# [2026-01-20T11:23:57.590365] Dynamic window timer elapsed; tick='3'
# [2026-01-20T11:23:57.744750] Releasing dynamic part of the window; dynamic_window_to_be_released='20000', location='#unknown'
# [2026-01-20T11:23:57.744750] Releasing dynamic part of the window; dynamic_window_to_be_released='20000', location='#unknown'
# [2026-01-20T11:23:57.744750] Releasing dynamic part of the window; dynamic_window_to_be_released='20000', location='#unknown'
# [2026-01-20T11:23:57.744750] Releasing dynamic part of the window; dynamic_window_to_be_released='20000', location='#unknown'
# [2026-01-20T11:23:57.744750] Releasing dynamic part of the window; dynamic_window_to_be_released='20000', location='#unknown'
