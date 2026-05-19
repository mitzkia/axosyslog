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
from pathlib import Path

from axosyslog_light.common.file import copy_shared_file
from axosyslog_light.syslog_ng_config.__init__ import stringify


input_message_file_name = Path("input_message.txt")
file_dst_output_name = Path("file_dst_output.txt")


def build_modifier(modifier, config, config_statements, input_msg):
    if modifier == "csv-parser-delimiter":
        modifier = config.create_csv_parser(prefix=config.stringify("prefix."), delimiters=config.stringify("|"))

    if modifier == "csv-parser-columns":
        number_of_delimiters = input_msg.count("|")
        column_names = ", ".join(f"'{i + 1}'" for i in range(number_of_delimiters + 1))
        modifier = config.create_csv_parser(prefix=config.stringify("prefix."), columns=column_names, delimiters=config.stringify("|"))

    config_statements.append(modifier)
    return config_statements


def build_filterx_rule(filterx_rule, config, config_statements, sample_log):
    filterx_expr = ""
    if filterx_rule == "filterx-parse-csv":
        filterx_expr += "$log = parse_csv($MSG, delimiter=',');\n"
        filterx_expr += "$MESSAGE = $log;"

    filterx = config.create_filterx(filterx_expr)
    config_statements.append(filterx)
    return config_statements


def set_filterx_for_parse(config, config_statements, testcase_parameters):
    filterx_expr = """
serialized_message = {
    "MSG_DATA_json": $MSG,
};
$protobuf_message = protobuf_message(serialized_message, schema_file="clickhouse_filterx_parse.proto");
$MESSAGE = {"message": serialized_message};
        """
    filterx = config.create_filterx(filterx_expr)
    config_statements.append(filterx)
    copy_shared_file(testcase_parameters, "clickhouse_filterx_parse.proto")


def build_clickhouse_config_options(destination, clickhouse_ports):
    clickhouse_options = {
        "database": "default",
        "table": "test_table",
        "user": "default",
        "password": f'{stringify("password")}',
        "url": f"'127.0.0.1:{clickhouse_ports.grpc_port}'",
        "workers": 4,
        "batch_lines": 1000,
        "batch_timeout": 1000,
        "log_fifo_size": 100000,
    }
    if destination == "clickhouse-dst-for-filterx-parse":
        clickhouse_options.update({
            "server_side_schema": "'clickhouse_filterx_parse:TestPerfProto'",
            "proto_var": "$protobuf_message",
        })
    else:
        clickhouse_options.update({
            "schema": '"message" "String" => "$MSG"',
        })
    return clickhouse_options


def create_clickhouse_table_for_destination_case(destination, clickhouse_destination, clickhouse_options, request):
    if destination == "clickhouse-dst-for-filterx-parse":
        clickhouse_destination.create_table(
            clickhouse_options["table"], [
                ("MSG_DATA_json", "Map(String, String)"),
            ],
        )
    else:
        clickhouse_destination.create_table(clickhouse_options["table"], [("message", "String")])
    request.addfinalizer(lambda: clickhouse_destination.delete_table())


def build_destination(destination, config, config_statements, clickhouse_server, clickhouse_ports, request, testcase_parameters):
    destination_driver = None

    if "clickhouse-dst" in destination:
        clickhouse_options = build_clickhouse_config_options(destination, clickhouse_ports)
        clickhouse_destination = config.create_clickhouse_destination(**clickhouse_options)
        clickhouse_destination.create_clickhouse_client(clickhouse_ports.http_port)
        destination_driver = clickhouse_destination
        config_statements.append(clickhouse_destination)
        clickhouse_server.start(clickhouse_ports)
        create_clickhouse_table_for_destination_case(destination, clickhouse_destination, clickhouse_options, request)

    return config_statements, destination_driver


def build_performance_test_config(config, config_start_params, request, testcase_parameters, sample_log):
    destination = config_start_params["destination"]
    filterx_rule = config_start_params["filterx_rule"]
    flow_control = config_start_params["flow_control"]
    port_allocator = config_start_params["port_allocator"]
    clickhouse_server = config_start_params["clickhouse_server"]
    clickhouse_ports = config_start_params["clickhouse_ports"]
    config_statements = []

    # global options
    config.update_global_options(stats_level=2)

    # source driver
    network_source = config.create_network_source(ip="localhost", port=port_allocator(), transport="tcp", log_iw_size=10000000, log_fetch_limit=100000, max_connections=10)
    config_statements.append(network_source)

    # filterx rule
    if filterx_rule:
        config_statements = build_filterx_rule(filterx_rule, config, config_statements, sample_log)

    # destination driver
    destination_driver = None
    if destination != "empty":
        config_statements, destination_driver = build_destination(destination, config, config_statements, clickhouse_server, clickhouse_ports, request, testcase_parameters)

    # logpath
    if "on" in flow_control or "yes" in flow_control or "enabled" in flow_control:
        config.create_logpath(statements=config_statements, flags=["flow-control"])
    else:
        config.create_logpath(statements=config_statements)

    return config, network_source, destination_driver
