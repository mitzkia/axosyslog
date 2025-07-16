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
import logging

import clickhouse_connect
import psutil
from axosyslog_light.common.blocking import wait_until_true
from axosyslog_light.common.file import copy_shared_file
from axosyslog_light.executors.process_executor import ProcessExecutor

logger = logging.getLogger(__name__)


class ClickhouseServerExecutor():
    def __init__(self, testcase_parameters) -> None:
        self.process = None
        self.clickhouse_severs_ports = [8123, 9000, 9004, 9005, 9009, 9100]
        copy_shared_file(testcase_parameters, "clickhouse_server_config.xml")
        copy_shared_file(testcase_parameters, "clickhouse_users.xml")

    def start(self) -> None:
        command = [
            "clickhouse-server", "start",
            "--config-file", "clickhouse_server_config.xml",
        ]
        self.process = ProcessExecutor().start(command, "clickhouse_server.stdout", "clickhouse_server.stderr")
        self.wait_for_start()
        logger.info(f"Clickhouse server started with PID: {self.process.pid}")

    def stop(self) -> None:
        self.process.terminate()
        self.wait_for_stop()
        logger.info(f"Clickhouse server with PID {self.process.pid} terminated.")

    def get_open_ports(self) -> list[int]:
        if not self.process:
            raise RuntimeError("Clickhouse server process is not running.")

        connections = psutil.Process(psutil.Process(self.process.pid).children()[0].pid).net_connections(kind='inet')
        open_ports = sorted(set([conn.laddr.port for conn in connections if conn.laddr]))
        return open_ports

    def wait_for_start(self) -> bool:
        assert wait_until_true(lambda: len(psutil.Process(self.process.pid).children()) > 0)
        assert wait_until_true(lambda: self.get_open_ports() == self.clickhouse_severs_ports), "Actual ports: {}, expected: {}".format(self.get_open_ports(), self.clickhouse_severs_ports)

    def wait_for_stop(self) -> bool:
        assert wait_until_true(lambda: self.get_open_ports() == [])


class ClickhouseClient():
    def __init__(self) -> None:
        self.table_name = None
        self.host = 'localhost'
        self.username = 'default'
        self.password = 'password'

    def create_table(self, table_name: str, table_columns_and_types: list[tuple[str, str]] = None) -> None:
        prim_key_col_name = table_columns_and_types[0][0]
        self.table_name = table_name

        client = clickhouse_connect.get_client(host=self.host, username=self.username, password=self.password)
        columns_definition = ", ".join([f'"{col}" {typ}' for col, typ in table_columns_and_types])
        if "TIME" in columns_definition:
            enable_time_setting = "SET enable_time_time64_type = 1;"
            client.command(enable_time_setting)
        create_table_query = f"CREATE TABLE {table_name} ({columns_definition}) ENGINE MergeTree() PRIMARY KEY (%s);" % prim_key_col_name
        client.command(create_table_query)
        client.close()
        logger.info(f"Table created: {table_name} with {create_table_query}")

    def delete_table(self) -> None:
        if self.table_name:
            client = clickhouse_connect.get_client(host=self.host, username=self.username, password=self.password)
            client.command(f'DROP TABLE IF EXISTS {self.table_name};')
            client.close()
            logger.info(f"Table deleted: {self.table_name}")

    def select_all_from_table(self, table_name: str) -> list:
        client = clickhouse_connect.get_client(host=self.host, username=self.username, password=self.password)
        query = f"SELECT * FROM {table_name};"
        query_res = client.command(query)
        client.close()
        logger.info(f"Query result: {query_res}")
        return query_res

    def run_query(self, query: str) -> None:
        client = clickhouse_connect.get_client(host=self.host, username=self.username, password=self.password)
        query_result = client.command(query)
        client.close()
        return query_result
