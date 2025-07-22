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
import datetime
import logging
import time

from axosyslog_light.common.blocking import wait_until_true_custom
from axosyslog_light.common.file import copy_shared_file
from axosyslog_light.helpers.loggen.loggen import LoggenStartParams

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

clickhouse_valid_options = {
    "database": "default",
    "table": "test_table",
    "user": "default",
    "password": "'password'",
    "schema": '"message" "String" => "$MESSAGE"',
    "workers": 1,
    "batch_lines": 50000,
    "batch_timeout": 5,
    "disk-buffer": {
        # "disk-buf-size": 10000000,  # 10 MB
        "mem-buf-length": 100000,      # 1000 messages in memory
        "mem-buf-size": 1000000,     # 1 MB in memory
    },
}


def test_clickhouse_destination_perf_generic_padd(config, syslog_ng, clickhouse_server, clickhouse_client, port_allocator, loggen):
    network_source = config.create_network_source(ip="localhost", port=port_allocator(), transport="tcp", log_iw_size=10000, log_fetch_limit=1000)
    clickhouse_destination = config.create_clickhouse_destination(**clickhouse_valid_options)
    config.create_logpath(statements=[network_source, clickhouse_destination])

    MSG_COUNTER = 2000000

    clickhouse_server.start()
    clickhouse_client.create_table("test_table", [("message", "String")])

    syslog_ng.start_params.trace = False
    syslog_ng.start_params.debug = False
    syslog_ng.start_params.verbose = False

    syslog_ng.start(config)
    time.sleep(1)

    loggen.start(
        LoggenStartParams(
            target=network_source.options["ip"],
            port=network_source.options["port"],
            inet=True,
            perf=True,
            active_connections=1,
            number=MSG_COUNTER,
        ),
    )

    logger.info("AAA-1: actual datetime: %s" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    assert wait_until_true_custom(lambda: loggen.get_sent_message_count() == MSG_COUNTER, timeout=180)
    logger.info("AAA-2: actual datetime: %s" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    assert wait_until_true_custom(lambda: clickhouse_destination.get_stats()["written"] == MSG_COUNTER, timeout=180)
    logger.info("AAA-3: actual datetime: %s" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    assert clickhouse_client.run_query("SELECT COUNT(*) FROM test_table;") == MSG_COUNTER, f"Expected {MSG_COUNTER} messages"
    logger.info("AAA-4: actual datetime: %s" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    try:
        syslog_ng.stop()
    except Exception as e:
        logger.error(f"Error stopping syslog-ng: {e}")
        pass


def test_clickhouse_destination_perf_complex_filterx(testcase_parameters, config, syslog_ng, syslog_ng_ctl, clickhouse_server, clickhouse_client, port_allocator, loggen):
    config.update_global_options(stats_level=5)
    network_source = config.create_network_source(ip="localhost", port=port_allocator(), transport="tcp", log_iw_size=10000, log_fetch_limit=1000, flags=['dont-store-legacy-msghdr'])
    filterx = config.create_filterx(
        '''
    cols = ["data1", "data2", "data3", "data4", "data5", "data6", "data7", "data8"];
    input_message = $MESSAGE;
    parsed_message = parse_csv(input_message, columns=cols);
    parsed_message["data5"] = {"foo": "bar", "baz": {"key1": "value1", "key2": "value2"}};
    parsed_message["data6"] = {"test1": "value1", "example1": {"keyA1": "valueA", "keyB1": "valueB"}, "nested1": {"innerKey1": "innerValue1", "innerKey2": "innerValue2"}};
    parsed_message["data7"] = {"test2": "value2", "example2": {"keyA2": "valueA", "keyB2": "valueB"}, "nested2": {"innerKey2": "innerValue1", "innerKey3": "innerValue2"}, "extra": "data"};
    parsed_message["data8"] = {"test3": "value3", "example3": {"keyA3": "valueA", "keyB3": "valueB"}, "nested3": {"innerKey4": "innerValue1", "innerKey5": "innerValue2"}, "additional": "info"};
    $protobuf_message = protobuf_message(parsed_message, schema_file="clickhouse_perf.proto");
    $MESSAGE = {"message": parsed_message};

''',
    )

    clickhouse_options = clickhouse_valid_options.copy()
    clickhouse_options.update({
        "server_side_schema": "'clickhouse_perf:TestPerfProto'",
        "proto_var": "$protobuf_message",
    })
    clickhouse_options.pop('schema', None)
    clickhouse_destination = config.create_clickhouse_destination(**clickhouse_options)
    config.create_logpath(statements=[network_source, filterx, clickhouse_destination])

    input_message_file_name = "input_message.txt"
    with open(input_message_file_name, "w") as f:
        f.write(
            "<113>Jul 17 14:47:40 testhost testprog 1,2025/07/17 14:47:40,012345678901,AAAA,"
            "randStrA1,2025-07-17T14:47:40.123456,9876543210,,"
            "loremipsu,"
            "minimveni,"
            "dolorirur,"
            "occaecatc,"
            "randStrB2,2025-07-17 14:47:40,1234567890,,"
            "randStrC3,2025/07/17 14:47:40,42,,"
            "EndMsg,"
            "RSTR1,2024-12-31 23:59:59,1001,,"
            "RSTR2,2023-01-01 00:00:00,2002,,"
            "RSTR3,2022-06-15 12:34:56,3003,,\n",
        )

    MSG_COUNTER = 2000000

    copy_shared_file(testcase_parameters, "clickhouse_perf.proto")
    clickhouse_server.start()

    clickhouse_client.create_table(
        "test_table", [
            ("data1", "String"),
            ("data2", "String"),
            ("data3", "String"),
            ("data4", "String"),
            ("data5", "Map(String, String)"),
            ("data6", "Map(String, String)"),
            ("data7", "Map(String, String)"),
            ("data8", "Map(String, String)"),
        ],
    )

    syslog_ng.start_params.trace = False
    syslog_ng.start_params.debug = False
    syslog_ng.start_params.verbose = False

    syslog_ng.start(config)
    time.sleep(1)

    loggen.start(
        LoggenStartParams(
            target=network_source.options["ip"],
            port=network_source.options["port"],
            inet=True,
            perf=True,
            active_connections=1,
            number=MSG_COUNTER,
            read_file=input_message_file_name,
            dont_parse=True,
            loop_reading=True,
        ),
    )

    time.sleep(1)
    assert wait_until_true_custom(lambda: loggen.get_sent_message_count() == MSG_COUNTER, timeout=180)
    assert wait_until_true_custom(lambda: clickhouse_destination.get_stats()["written"] == MSG_COUNTER, timeout=180)
    assert clickhouse_client.run_query("SELECT COUNT(*) FROM test_table;") == MSG_COUNTER, f"Expected {MSG_COUNTER} messages"

    logger.info(syslog_ng_ctl.stats_prometheus())

    try:
        syslog_ng.stop()
    except Exception as e:
        logger.error(f"Error stopping syslog-ng: {e}")
        pass

    # query_res = clickhouse_client.run_query(f"SELECT * FROM test_table;")
    # logger.info(f"Query result: {query_res}")
