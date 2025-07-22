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
import re
import string

from axosyslog_light.common.file import copy_shared_file

# input_string = string.ascii_letters + string.digits + "{}[]()<>'\"/\\,.-=+_!@#$%^&*``~|?:; \n\t\r" + "\u00A0"  + "Árvíztűrő tükörfúrógép"
# input_string = string.ascii_letters + string.digits + "Árvíztűrő tükörfúrógép" + "\u00A0" + ".,;:!?@#$%^&*_+-=~|[]{}()<>``\n\t\r"
input_string = string.ascii_letters + string.digits + "Árvíztűrő tükörfúrógép" + ".,;:!?@#$%^&*_+-=~|[]{}()<>``\n\t\r"

logger = logging.getLogger(__name__)


clickhouse_data_type_values = [
    # (axosyslog_data_type, input_value)
    ("Int8", -128),
    ("TINYINT", 127),
    ("INT1", -128),
    ("TINYINT SIGNED", 127),
    ("INT1 SIGNED", -128),
    # ("UInt8", 255),
    # ("TINYINT UNSIGNED", 255),
    # ("INT1 UNSIGNED", 255),
    ("Int16", -32768),
    ("SMALLINT", 32767),
    ("SMALLINT SIGNED", -32768),
    ("UInt16", 65535),
    ("SMALLINT UNSIGNED", 65535),
    ("Int32", -2147483648),
    ("INT", 2147483647),
    ("INTEGER", -2147483648),
    ("MEDIUMINT", 2147483647),
    ("MEDIUMINT SIGNED", -2147483648),
    ("INT SIGNED", 2147483647),
    ("INTEGER SIGNED", -2147483648),
    ("UInt32", 4294967295),
    ("MEDIUMINT UNSIGNED", 4294967295),
    ("INT UNSIGNED", 4294967295),
    ("INTEGER UNSIGNED", 4294967295),
    ("Int64", -9223372036854775808),
    ("BIGINT", 9223372036854775807),
    ("SIGNED", -9223372036854775808),
    ("BIGINT SIGNED", 9223372036854775807),
    ("UInt64", 18446744073709551615),
    ("UNSIGNED", 18446744073709551615),
    ("BIGINT UNSIGNED", 18446744073709551615),
    ("BIT", 18446744073709551615),
    ("SET", 18446744073709551615),
    ("Float32", 3.4028235e38),
    ("FLOAT", 3.4028235e38),
    ("REAL", 3.4028235e38),
    ("SINGLE", 3.4028235e38),
    ("Float64", 1.7976931348623157e308),
    ("DOUBLE", 1.7976931348623157e308),
    ("DOUBLE PRECISION", 1.7976931348623157e308),
    ("BINARY LARGE OBJECT", input_string),
    ("BINARY VARYING", input_string),
    ("BLOB", input_string),
    ("CHAR LARGE OBJECT", input_string),
    ("CHAR VARYING", input_string),
    ("CHAR", input_string),
    ("CHARACTER LARGE OBJECT", input_string),
    ("CHARACTER VARYING", input_string),
    ("LONGBLOB", input_string),
    ("LONGTEXT", input_string),
    ("MEDIUMBLOB", input_string),
    ("MEDIUMTEXT", input_string),
    ("NATIONAL CHAR VARYING", input_string),
    ("NATIONAL CHAR", input_string),
    ("NATIONAL CHARACTER LARGE OBJECT", input_string),
    ("NATIONAL CHARACTER VARYING", input_string),
    ("NATIONAL CHARACTER", input_string),
    ("NCHAR LARGE OBJECT", input_string),
    ("NCHAR VARYING", input_string),
    ("String", input_string),
    ("TEXT", input_string),
    ("TINYBLOB", input_string),
    ("TINYTEXT", input_string),
    ("VARCHAR", input_string),
    ("BOOL", True),
    ("BOOL", 0),
    # ("Enum('value1')", 'value1'),
    # ("Enum16('value1')", "value1"),
    # ("Enum8('value1')", "value1"),
    ("UUID", "550e8400-e29b-41d4-a716-446655440000"),
    ("IPv4", "255.255.255.255"),
    # ("IPv6", "::"),
    # ("IPv6", "ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff"),
    # ("TIME", '100:00:00'),
    # ("TIME", 12453),
    # ("DATE", '2019-01-01'),
    ("DATE", 17897),
    # ("DATE", 1546300800),
    # ("DATE32", '2100-01-01'),
    ("DATE32", 47482),
    ("DATE32", 4102444800),
    # ("DateTime('Europe/Budapest')", '2019-01-01 00:00:00'),
    ("DateTime('Europe/Budapest')", 1546300800),
    # ("DateTime64(3, 'Europe/Budapest')", 1546300800123),
    # ("DateTime64(3, 'Europe/Budapest')", 1546300800.123),
    # ("DateTime64(3, 'Europe/Budapest')", '2019-01-01 00:00:00'),
]


def column_iterator():
    for idx, value in enumerate(clickhouse_data_type_values):
        col_name = f"col_{value[0].replace(" ", "_")}_{idx}"
        col_name_without_inner_def = re.sub(r"\('.*'\)", "", col_name)
        col_type = value[0]
        col_type_without_inner_def = re.sub(r"\('.*'\)", "", col_type)
        col_value = value[1]
        yield col_name_without_inner_def, col_type, col_type_without_inner_def, col_value


def build_input_message():
    input_message = {"ID": 1}
    for col_name, _, col_type, col_value in column_iterator():
        input_message[col_name] = col_value

    return input_message


def build_filterx_expression():
    filterx_expression = "$ID = json($MSG).ID;\n"
    for col_name, _, col_type, col_value in column_iterator():
        filterx_expression += f"${col_name} = json($MSG).{col_name};\n"

    return filterx_expression


def build_clickhouse_schema_expression():
    clickhouse_schema_expression = '"ID" "Integer" => "$ID",\n'
    for col_name, _, col_type, col_value in column_iterator():
        clickhouse_schema_expression += f'"{col_name}" "{col_type}" => ${col_name},\n'

    return clickhouse_schema_expression


def build_clickhouse_column_definitions():
    column_definitions = [("ID", "Integer")]
    for col_name, col_type, _, col_value in column_iterator():
        column_definitions.append((col_name, col_type))

    return column_definitions


def get_expected_result():
    expected_result = ['1']
    for col_name, _, _, col_value in column_iterator():
        if "BOOL" in col_name and col_value is True:
            col_value = 'true'
        elif "BOOL" in col_name and col_value == 0:
            col_value = 'false'
        elif "e+" in str(col_value):
            col_value = str(col_value).replace("e+", "e")
        elif "\n" in str(col_value):
            col_value = col_value.replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t").replace("``", "`")
        elif "DATE" in col_name and col_value == 17897:
            col_value = '2019-01-01'
        elif "DATE32" in col_name and col_value == 47482:
            col_value = '2100-01-01'
        elif "DATE32" in col_name and col_value == 4102444800:
            col_value = '2100-01-01'
        elif "DateTime" in col_name and col_value == 1546300800:
            col_value = '2019-01-01 00:00:00'

        expected_result.append(str(col_value))
    return expected_result


def test_clickhouse_destination_basic_types(testcase_parameters, config, syslog_ng, clickhouse_server, clickhouse_client):
    table_name = "test_table_1"

    generator_source = config.create_example_msg_generator_source(
        num=1,
        template=config.stringify(str(build_input_message())),
    )
    filterx = config.create_filterx(build_filterx_expression())
    clickhouse_destination = config.create_clickhouse_destination(
        database="default",
        table=table_name,
        user="default",
        password="'password'",
        schema=build_clickhouse_schema_expression(),
    )
    config.create_logpath(statements=[generator_source, filterx, clickhouse_destination])

    clickhouse_server.start()
    clickhouse_client.create_table(table_name, build_clickhouse_column_definitions())

    syslog_ng.start(config)

    query_res = clickhouse_client.run_query(f"SELECT * FROM {table_name}")

    assert clickhouse_destination.get_stats()["written"] == 1
    assert query_res == get_expected_result()


def test_clickhouse_destination_nested_types(testcase_parameters, config, syslog_ng, clickhouse_server, clickhouse_client):
    table_name = "test_table_2"

    generator_source = config.create_example_msg_generator_source(
        num=1,
        template=config.stringify("<34>Oct 11 22:14:15 mymachine su: 'su root' failed for lonvick on /dev/pts/8"),
    )
    message_schema = '''{
    "name": $MESSAGE,
    "id": int($R_MSEC),
    "foobar": {
        "host": $HOST,
        "time":string($R_UNIXTIME),
        "date": string($FULLDATE)
    },
    "arr": ["foo", "bar", "baz", {"map": {"key": "value"}}],
    "sub": {
        "foo": "value11",
        "bar": "value21"
    },
    "repsub": [{
        "foo": "value12",
        "bar": "value22"
    }, {
        "foo": "value33",
        "bar": "value43"
    }],
};'''

    filterx = config.create_filterx(
        '''
        message = %s
        $protobuf_message = protobuf_message(message, schema_file="clickhouse.proto");
        $MESSAGE = {"message": message};
    ''' % (message_schema),
    )
    clickhouse_destination = config.create_clickhouse_destination(
        database="default",
        table=table_name,
        user="default",
        password="'password'",
        server_side_schema="'clickhouse:TestProto'",
        proto_var="$protobuf_message",
    )
    config.create_logpath(statements=[generator_source, filterx, clickhouse_destination])

    copy_shared_file(testcase_parameters, "clickhouse.proto")
    clickhouse_server.start()
    clickhouse_client.create_table(
        table_name, [
            ("name", "LowCardinality(String)"),
            ("id", "Int32"),
            ("foobar", "Map(String, String)"),
            ("arr", "Array(String)"),
            ("sub", "Tuple(foo String, bar String, baz String)"),
            ("repsub", "Array(Tuple(foo String, bar String, baz String))"),
        ],
    )

    syslog_ng.start(config)

    query_res = clickhouse_client.run_query(f"SELECT * FROM {table_name}")
    logger.info(f"Query result: {query_res}")

    assert clickhouse_destination.get_stats()["written"] == 1

    assert query_res == ["<34>Oct 11 22:14:15 mymachine su: \\'su root\\' failed for lonvick on /dev/pts/8", '432', "{'host':'micek-ThinkPad-T14-Gen-4','time':'1752588976.000000','date':'2025 Jul 15 14:16:16'}", '[\'foo\',\'bar\',\'baz\',\'{"map":{"key":"value"}}\']', "('value11','value21','')", "[('value12','value22',''),('value33','value43','')]"]
