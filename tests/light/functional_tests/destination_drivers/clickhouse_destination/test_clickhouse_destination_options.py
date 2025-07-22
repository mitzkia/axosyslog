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
from axosyslog_light.common.file import copy_shared_file

clickhouse_valid_options = {
    "database": "default",
    "table": "test_table",
    "user": "default",
    "password": "'password'",
    "schema": '"message" "String" => "$MSG"',
}


def test_clickhouse_destination_valid_options_db_run(config, syslog_ng, clickhouse_server, clickhouse_client):
    custom_input_msg = f"test message {str(uuid.uuid4())}"
    generator_source = config.create_example_msg_generator_source(num=1, template=f'"{custom_input_msg}"')
    clickhouse_destination = config.create_clickhouse_destination(**clickhouse_valid_options)
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
    clickhouse_destination = config.create_clickhouse_destination(**clickhouse_valid_options)
    config.create_logpath(statements=[generator_source, clickhouse_destination])

    syslog_ng.start(config)

    assert clickhouse_destination.get_stats()["written"] == 0

    assert syslog_ng.wait_for_message_in_console_log("Message added to ClickHouse batch") != []
    assert syslog_ng.wait_for_message_in_console_log("ClickHouse server responded with a temporary error status code") != []


def test_clickhouse_destination_valid_url_option_db_run(config, syslog_ng, clickhouse_server, clickhouse_client):
    custom_input_msg = f"test message {str(uuid.uuid4())}"
    generator_source = config.create_example_msg_generator_source(num=1, template=f'"{custom_input_msg}"')
    clickhouse_options = clickhouse_valid_options.copy()
    clickhouse_options.update({"url": "'127.0.0.1:9100'"})
    clickhouse_destination = config.create_clickhouse_destination(**clickhouse_options)
    config.create_logpath(statements=[generator_source, clickhouse_destination])

    clickhouse_server.start()
    clickhouse_client.create_table("test_table", [("message", "String")])

    syslog_ng.start(config)

    assert clickhouse_destination.get_stats()["written"] >= 1

    db_logs = clickhouse_destination.read_logs()
    assert db_logs == custom_input_msg


invalid_url_values = [
    ("'localhost'"),  # Missing port
    ("'invalid-domain:1234'"),  # Invalid domain
    ("'localhost:9100,localhost:9000'"),  # Multiple URLs not supported
    ("'@#@!#$RFSDSVCWRF SFsd'"),  # Garbage string
    ("' '"),  # Whitespace only
    ("'127.0.0.1'"),  # IPv4 address without port
    ("'::1'"),  # IPv6 address without port
]


@pytest.mark.parametrize("invalid_option_value", invalid_url_values, ids=range(len(invalid_url_values)))
def test_clickhouse_destination_invalid_url_option_db_run(config, syslog_ng, clickhouse_server, clickhouse_client, invalid_option_value):
    custom_input_msg = f"test message {str(uuid.uuid4())}"
    generator_source = config.create_example_msg_generator_source(num=1, template=f'"{custom_input_msg}"')
    clickhouse_options = clickhouse_valid_options.copy()
    clickhouse_options.update({"url": invalid_option_value})
    clickhouse_destination = config.create_clickhouse_destination(**clickhouse_options)
    config.create_logpath(statements=[generator_source, clickhouse_destination])

    clickhouse_server.start()
    clickhouse_client.create_table("test_table", [("message", "String")])

    syslog_ng.start(config)

    assert clickhouse_destination.get_stats()["written"] == 0


@pytest.mark.parametrize(
    "ch_database, ch_table, ch_user, ch_password", [
        ("invalid_dababase", "test_table", "default", "'password'"),
        ("default", "invalid_table", "default", "'password'"),
        ("default", "test_table", "invalid_user", "'password'"),
        ("default", "test_table", "default", "'invalid_password'"),
    ], ids=["invalid_database", "invalid_table", "invalid_user", "invalid_password"],
)
def test_clickhouse_destination_invalid_options_db_run(config, syslog_ng, clickhouse_server, clickhouse_client, ch_database, ch_table, ch_user, ch_password):
    custom_input_msg = f"test message {str(uuid.uuid4())}"
    generator_source = config.create_example_msg_generator_source(num=1, template=f'"{custom_input_msg}"')
    clickhouse_destination = config.create_clickhouse_destination(database=ch_database, table=ch_table, user=ch_user, password=ch_password, schema='"message" "String" => "$MSG"')
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
        clickhouse_options.update({"database": ch_database})
    if ch_table is not None:
        clickhouse_options.update({"table": ch_table})
    if ch_user is not None:
        clickhouse_options.update({"user": ch_user})
    clickhouse_options.update({"schema": '"message" "String" => "$MSG"'})

    clickhouse_destination = config.create_clickhouse_destination(**clickhouse_options)
    config.create_logpath(statements=[generator_source, clickhouse_destination])

    with pytest.raises(Exception) as exec_info:
        syslog_ng.start(config)
    assert "syslog-ng is not running" in str(exec_info.value)
    assert syslog_ng.wait_for_message_in_console_log("Error initializing ClickHouse destination, database(), table() and user() are mandatory options") != []


invalid_schema_values = [
    ('', "syslog-ng is not running"),  # Example: empty schema string
    (' ', "syslog-ng is not running"),  # Example: whitespace only
    (' => ', "syslog-ng config syntax error"),  # Example: only mapping operator
    ('some random string 1234', "syslog-ng config syntax error"),  # Example: some random value
    ('"id" "String" =>', "syslog-ng config syntax error"),  # Example: missing message macro
    ('"id" "String" $MSG', "syslog-ng config syntax error"),  # Example: missing mapping operator
    ('"id", "String" => $MSG', "start passed"),  # Example: comma separator
    ('"id" "String" => $MSG, "id2 id3" "String" => $MSG', "syslog-ng is not running"),  # Example: second invalid, crash
    ('id String => $MSG', "start passed"),  # Example: values without quotes
    ('"id" "String" => $NotAvailableMacro', "start passed"),  # Example: not available macro
    ('"id" "String" => MSG', "start passed"),  # Example: missing $ in message macro
    ('"$id" "String" => $MSG', "syslog-ng is not running"),  # Example: $ in column name, crash
    ('"$id $id2" "String" => $MSG', "syslog-ng is not running"),  # Example: $ in column name, crash
    ('"id" => $MSG', "start passed"),  # Example: missing type
    ('"String" => $MSG', "start passed"),  # Example: missing column name
    ('"id" "String" => => $MSG', "syslog-ng config syntax error"),  # Example: double mapping operator
    ('"id" "String" => $MSG => $MSG', "syslog-ng config syntax error"),  # Example: double mapping operator and message macro
    ('"id" "UnknownType" => $MSG', "syslog-ng config syntax error"),  # Example: invalid type
    ('"id id2" "String" => $MSG', "syslog-ng is not running"),  # Example: double column, crash
    ('"id" "String Integer" => $MSG', "syslog-ng config syntax error"),  # Example: double type
    ('"id" "String" => $MSG $DATE', "syslog-ng config syntax error"),  # Example: double message macro
    ('"event_time" "DateTime" => "$YEAR-$MONTH-$DAY $HOUR:$MIN:$SEC"', "start passed"),  # Example: valid mapping with DateTime
]


@pytest.mark.parametrize("option_value, expected_error", invalid_schema_values, ids=range(len(invalid_schema_values)))
def test_clickhouse_destination_invalid_schema_option(testcase_parameters, config, syslog_ng, option_value, expected_error):
    generator_source = config.create_example_msg_generator_source(num=1)
    clickhouse_options = {
        "database": "default",
        "table": "test_table",
        "user": "default",
    }
    clickhouse_options.update({"schema": option_value})
    clickhouse_destination = config.create_clickhouse_destination(**clickhouse_options)
    config.create_logpath(statements=[generator_source, clickhouse_destination])

    if expected_error != "start passed":
        with pytest.raises(Exception) as exec_info:
            syslog_ng.start(config)
        assert expected_error in str(exec_info.value)
    else:
        syslog_ng.start(config)


invalid_protobuf_schema_values = [
    ('', 'syslog-ng config syntax error'),
    (' ', 'syslog-ng config syntax error'),
    ('"clickhouse.proto" => "$MSG", "$AAA"', 'syslog-ng config syntax error'),
    ('"clickhouse.proto" => "$MSG" "$AAA"', 'syslog-ng config syntax error'),
    ('"clickhouse.proto" "$MSG" "$AAA"', 'syslog-ng config syntax error'),
    ('=> "$MSG" "$AAA"', 'syslog-ng config syntax error'),
    ('"$MSG" "$AAA"', 'syslog-ng config syntax error'),
]


@pytest.mark.parametrize("invalid_protobuf_schema_value, expected_error", invalid_protobuf_schema_values, ids=range(len(invalid_protobuf_schema_values)))
def test_clickhouse_destination_invalid_protobuf_schema_option(testcase_parameters, config, syslog_ng, invalid_protobuf_schema_value, expected_error):
    generator_source = config.create_example_msg_generator_source(num=1)
    clickhouse_options = clickhouse_valid_options.copy()
    clickhouse_options.update({"protobuf_schema": invalid_protobuf_schema_value})
    clickhouse_destination = config.create_clickhouse_destination(**clickhouse_options)
    config.create_logpath(statements=[generator_source, clickhouse_destination])

    with pytest.raises(Exception) as exec_info:
        syslog_ng.start(config)
    assert expected_error in str(exec_info.value)


invalid_server_side_schema_values = [
    ('', 'syslog-ng config syntax error'),
    (' ', 'syslog-ng config syntax error'),
    ('"invalid:invalid"', ''),
    ('"invalid.invalid"', ''),
    ('"invalid@invalid"', ''),
]


@pytest.mark.parametrize("invalid_server_side_schema_value, expected_error", invalid_server_side_schema_values, ids=range(len(invalid_server_side_schema_values)))
def test_clickhouse_destination_invalid_server_side_schema_option(testcase_parameters, config, syslog_ng, clickhouse_server, clickhouse_client, invalid_server_side_schema_value, expected_error):
    generator_source = config.create_example_msg_generator_source(num=1)
    clickhouse_options = clickhouse_valid_options.copy()
    clickhouse_options.update({"server_side_schema": invalid_server_side_schema_value})
    clickhouse_destination = config.create_clickhouse_destination(**clickhouse_options)
    config.create_logpath(statements=[generator_source, clickhouse_destination])

    clickhouse_server.start()
    clickhouse_client.create_table("test_table", [("message", "String")])

    if expected_error:
        with pytest.raises(Exception) as exec_info:
            syslog_ng.start(config)
        assert expected_error in str(exec_info.value)
    else:
        syslog_ng.start(config)
        assert clickhouse_destination.get_stats() == {'eps_last_1h': 0, 'eps_since_start': 0, 'processed': 1, 'msg_size_avg': 27, 'eps_last_24h': 0, 'batch_size_max': 0, 'dropped': 1, 'queued': 0, 'written': 0, 'memory_usage': 0, 'batch_size_avg': 0, 'msg_size_max': 27}


invalid_proto_var_values = [
    ('protobuf_message({"": ""}, schema_file="clickhouse.proto")', 'filterx error'),  # unknown field name
    ('protobuf_message({"name": $AAA}, schema_file="clickhouse.proto")', 'filterx error'),  # Variable is unset
    ('protobuf_message({"name": None}, schema_file="clickhouse.proto")', 'filterx error'),  # No such variable
    ('protobuf_message({"name": 123}, schema_file="clickhouse.proto")', 'filterx error'),  # Type for field name is unsupported
    ('protobuf_message', 'filterx error'),  # No such variable
    # ##############
    ('protobuf_message({"name": "fsdfsdf}, schema_file="clickhouse.proto")', 'syntax error'),
    ('protobuf_message()', 'syntax error'),
    ('protobuf_message({"name": "value"}, schema_file="")', "syntax error"),
    ('protobuf_message({"name": "value"}, schema_file="clickhouse.proto", extra_arg=1)', 'syntax error'),
    ('', 'syntax error'),
    # #############
    ('123', 'LogMessage type is not protobuf'),
    ('{}', 'LogMessage type is not protobuf'),
    ('" "', 'LogMessage type is not protobuf'),
    ('0x00', 'LogMessage type is not protobuf'),
]


@pytest.mark.parametrize("invalid_proto_var_value, expected_error", invalid_proto_var_values, ids=range(len(invalid_proto_var_values)))
def test_clickhouse_destination_invalid_proto_var_option(testcase_parameters, config, syslog_ng, clickhouse_server, clickhouse_client, invalid_proto_var_value, expected_error):
    generator_source = config.create_example_msg_generator_source(
        num=1,
        template=config.stringify("<34>Oct 11 22:14:15 mymachine su: 'su root' failed for lonvick on /dev/pts/8"),
    )

    filterx = config.create_filterx(
        '''
        $invalid_proto_var_value = %s;
    ''' % (invalid_proto_var_value),
    )
    clickhouse_options = clickhouse_valid_options.copy()
    clickhouse_options.update({"proto_var": "$invalid_proto_var_value"})
    clickhouse_options.pop('schema', None)
    clickhouse_destination = config.create_clickhouse_destination(**clickhouse_options)
    config.create_logpath(statements=[generator_source, filterx, clickhouse_destination])

    copy_shared_file(testcase_parameters, "clickhouse.proto")
    clickhouse_server.start()
    clickhouse_client.create_table("test_table", [("message", "String")])

    if expected_error == "filterx error":
        syslog_ng.start(config)
        assert clickhouse_destination.get_stats()["written"] == 0
        assert syslog_ng.wait_for_message_in_console_log("FILTERX ERROR") != []
    elif expected_error == "syntax error":
        with pytest.raises(Exception) as exec_info:
            syslog_ng.start(config)
        assert "syslog-ng config syntax error" in str(exec_info.value)
    elif expected_error == "LogMessage type is not protobuf":
        syslog_ng.start(config)
        assert syslog_ng.wait_for_message_in_console_log("LogMessage type is not protobuf") != []
        assert clickhouse_destination.get_stats()["written"] == 0
