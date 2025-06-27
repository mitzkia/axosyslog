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
import uuid

import pytest


def test_clickhouse_destination_valid_options_db_run(config, syslog_ng, clickhouse_server, clickhouse_client):
    custom_input_msg = f"test message {str(uuid.uuid4())}"
    generator_source = config.create_example_msg_generator_source(num=1, template=f'"{custom_input_msg}"')
    clickhouse_destination = config.create_clickhouse_destination(database="default", table="test_table", user="default", schema='"message" "String" => "$MSG"')
    config.create_logpath(statements=[generator_source, clickhouse_destination])

    clickhouse_server.start()
    clickhouse_client.create_table("test_table", [("message", "String")])

    syslog_ng.start(config)

    assert clickhouse_destination.get_stats()["written"] >= 1

    db_logs = clickhouse_destination.read_logs()
    assert db_logs == custom_input_msg


def test_clickhouse_destination_valid_options_db_not_run(config, syslog_ng):
    custom_input_msg = f"test message {str(uuid.uuid4())}"
    generator_source = config.create_example_msg_generator_source(num=1, template=f'"{custom_input_msg}"')
    clickhouse_destination = config.create_clickhouse_destination(database="default", table="test_table", user="default", schema='"message" "String" => "$MSG"')
    config.create_logpath(statements=[generator_source, clickhouse_destination])

    syslog_ng.start(config)

    assert clickhouse_destination.get_stats()["written"] == 0

    assert syslog_ng.wait_for_message_in_console_log("Message added to ClickHouse batch") != []
    assert syslog_ng.wait_for_message_in_console_log("ClickHouse server responded with a temporary error status code") != []


@pytest.mark.parametrize(
    "ch_database, ch_table, ch_user", [
        ("invalid_dababase", "test_table", "default"),
        ("default", "invalid_table", "default"),
        ("default", "test_table", "invalid_user"),
    ], ids=["invalid_database", "invalid_table", "invalid_user"],
)
def test_clickhouse_destination_invalid_options_db_run(config, syslog_ng, clickhouse_server, clickhouse_client, ch_database, ch_table, ch_user):
    custom_input_msg = f"test message {str(uuid.uuid4())}"
    generator_source = config.create_example_msg_generator_source(num=1, template=f'"{custom_input_msg}"')
    clickhouse_destination = config.create_clickhouse_destination(database=ch_database, table=ch_table, user=ch_user, schema='"message" "String" => "$MSG"')
    config.create_logpath(statements=[generator_source, clickhouse_destination])

    clickhouse_server.start()
    clickhouse_client.create_table("test_table", [("message", "String")])

    syslog_ng.start(config)

    assert clickhouse_destination.get_stats()["written"] == 0

    assert syslog_ng.wait_for_message_in_console_log("Message added to ClickHouse batch") != []
    assert syslog_ng.wait_for_message_in_console_log("ClickHouse server responded with an exception") != []


@pytest.mark.parametrize(
    "ch_database, ch_table, ch_user", [
        (None, "test_table", "default"),
        ("default", None, "default"),
        ("default", "test_table", None),
    ], ids=["invalid_database", "invalid_table", "invalid_user"],
)
def test_clickhouse_destination_missing_options_db_run(config, syslog_ng, clickhouse_server, clickhouse_client, ch_database, ch_table, ch_user):
    custom_input_msg = f"test message {str(uuid.uuid4())}"
    generator_source = config.create_example_msg_generator_source(num=1, template=f'"{custom_input_msg}"')
    clickhouse_options = {}
    if ch_database is not None:
        clickhouse_options["database"] = ch_database
    if ch_table is not None:
        clickhouse_options["table"] = ch_table
    if ch_user is not None:
        clickhouse_options["user"] = ch_user
    clickhouse_options["schema"] = '"message" "String" => "$MSG"'

    clickhouse_destination = config.create_clickhouse_destination(**clickhouse_options)
    config.create_logpath(statements=[generator_source, clickhouse_destination])

    with pytest.raises(Exception) as exec_info:
        syslog_ng.start(config)
    assert "syslog-ng is not running" in str(exec_info.value)
    assert syslog_ng.wait_for_message_in_console_log("Error initializing ClickHouse destination, database(), table() and user() are mandatory options") != []


invalid_schema_values = [
    (''),  # Example: empty schema string
    (' '),  # Example: whitespace only
    (' => '),  # Example: only mapping operator
    ('some random string 1234'),  # Example: some random value
    ('"id" "String" =>'),  # Example: missing message macro
    ('"id" "String" $MSG'),  # Example: missing mapping operator
    ('"id", "String" => $MSG'),  # Example: comma separator
    ('"id" "String" => $MSG, "id2 id3" "String" => $MSG'),  # Example: second invalid
    ('id String => $MSG'),  # Example: values without quotes
    ('"id" "String" => $NotAvailableMacro'),  # Example: not available macro
    ('"id" "String" => MSG'),  # Example: missing $ in message macro
    ('"$id" "String" => $MSG'),  # Example: $ in column name
    ('"$id $id2" "String" => $MSG'),  # Example: $ in column name
    ('"id" => $MSG'),  # Example: missing type
    ('"String" => $MSG'),  # Example: missing column name
    ('"id" "String" => => $MSG'),  # Example: double mapping operator
    ('"id" "String" => $MSG => $MSG'),  # Example: double mapping operator and message macro
    ('"id" "UnknownType" => $MSG'),  # Example: invalid type
    ('"id id2" "String" => $MSG'),  # Example: double column
    ('"id" "String Integer" => $MSG'),  # Example: double type
    ('"id" "String" => $MSG $DATE'),  # Example: double message macro
    ('"event_time" "DateTime" => "$YEAR-$MONTH-$DAY $HOUR:$MIN:$SEC"'),  # Example: valid mapping with DateTime
]


@pytest.mark.parametrize("option_value", invalid_schema_values, ids=range(len(invalid_schema_values)))
def test_clickhouse_destination_invalid_schema_option(testcase_parameters, config, syslog_ng, option_value):
    generator_source = config.create_example_msg_generator_source(num=1)
    clickhouse_options = {
        "database": "default",
        "table": "test_table",
        "user": "default",
    }
    clickhouse_options["schema"] = option_value
    clickhouse_destination = config.create_clickhouse_destination(**clickhouse_options)
    config.create_logpath(statements=[generator_source, clickhouse_destination])

    syslog_ng.start(config)


invalid_protobuf_schema_values = [
    ('', 'syslog-ng config syntax error'),
    (' ', 'syslog-ng config syntax error'),
    ('"clickhouse.proto" => "$MSG", "$AAA"', 'syslog-ng is not running'),
    ('"clickhouse.proto" => "$MSG" "$AAA"', 'syslog-ng is not running'),
    ('"clickhouse.proto" "$MSG" "$AAA"', 'syslog-ng config syntax error'),
    ('=> "$MSG" "$AAA"', 'syslog-ng config syntax error'),
    ('"$MSG" "$AAA"', 'syslog-ng config syntax error'),
]


@pytest.mark.parametrize("option_value, expected_error", invalid_protobuf_schema_values, ids=range(len(invalid_protobuf_schema_values)))
def test_clickhouse_destination_invalid_protobuf_schema_option(testcase_parameters, config, syslog_ng, option_value, expected_error):
    generator_source = config.create_example_msg_generator_source(num=1)
    clickhouse_options = {
        "database": "default",
        "table": "test_table",
        "user": "default",
    }
    clickhouse_options["protobuf_schema"] = option_value
    clickhouse_destination = config.create_clickhouse_destination(**clickhouse_options)
    config.create_logpath(statements=[generator_source, clickhouse_destination])

    with pytest.raises(Exception) as exec_info:
        syslog_ng.start(config)
    assert expected_error in str(exec_info.value)
