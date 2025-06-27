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
import time

import pytest
from axosyslog_light.common.file import copy_shared_file

column_schema = [
    ("id_bigint_signed", "BIGINT SIGNED", 1234567890123456789),
    ("id_bigint_unsigned", "BIGINT UNSIGNED", 12345678901234567890),
    ("id_bigint", "BIGINT", 1234567890123456789),
    # ("id_binary_large_object", "BINARY LARGE OBJECT", b"binarydata"),
    # ("id_binary_varying", "BINARY VARYING", b"varyingbinary"),
    ("id_bit", "BIT", 1),
    # ("id_blob", "BLOB", b"blobdata"),
    ("id_bool", "BOOL", True),
    ("id_char_large_object", "CHAR LARGE OBJECT", "char large object"),
    ("id_char_varying", "CHAR VARYING", "char varying"),
    ("id_char", "CHAR", "C"),
    ("id_character_large_object", "CHARACTER LARGE OBJECT", "character large object"),
    ("id_character_varying", "CHARACTER VARYING", "character varying"),
    # ("id_date", "DATE", "2024-01-01"),
    # ("id_date32", "DATE32", "2024-01-01"),
    # ("id_datetime", "DATETIME", "2024-01-01 12:34:56"),
    # ("id_datetime64", "DATETIME64", "2024-01-01 12:34:56.789"),
    ("id_double_precision", "DOUBLE PRECISION", 12345.6789),
    ("id_double", "DOUBLE", 12345.6789),
    ("id_enum", "ENUM", "value1"),
    ("id_enum16", "ENUM16", "value2"),
    ("id_enum8", "ENUM8", "value3"),
    ("id_float", "FLOAT", 123.45),
    ("id_float32", "FLOAT32", 123.45),
    ("id_float64", "FLOAT64", 12345.6789),
    ("id_int_signed", "INT SIGNED", -12345),
    ("id_int_unsigned", "INT UNSIGNED", 12345),
    ("id_int", "INT", 12345),
    ("id_int1_signed", "INT1 SIGNED", -1),
    ("id_int1_unsigned", "INT1 UNSIGNED", 1),
    ("id_int1", "INT1", 1),
    ("id_int16", "INT16", 12345),
    ("id_int32", "INT32", 123456789),
    ("id_int64", "INT64", 1234567890123456789),
    ("id_int8", "INT8", 127),
    ("id_integer_signed", "INTEGER SIGNED", -123456),
    ("id_integer_unsigned", "INTEGER UNSIGNED", 123456),
    ("id_integer", "INTEGER", 123456),
    ("id_ipv4", "IPV4", "192.168.1.1"),
    ("id_ipv6", "IPV6", "2001:0db8:85a3:0000:0000:8a2e:0370:7334"),
    # ("id_longblob", "LONGBLOB", b"longblobdata"),
    ("id_longtext", "LONGTEXT", "long text value"),
    # ("id_mediumblob", "MEDIUMBLOB", b"mediumblobdata"),
    ("id_mediumint_signed", "MEDIUMINT SIGNED", -8388608),
    ("id_mediumint_unsigned", "MEDIUMINT UNSIGNED", 16777215),
    ("id_mediumint", "MEDIUMINT", 8388607),
    ("id_mediumtext", "MEDIUMTEXT", "medium text value"),
    ("id_national_char_varying", "NATIONAL CHAR VARYING", "national char varying"),
    ("id_national_char", "NATIONAL CHAR", "N"),
    ("id_national_character_large_object", "NATIONAL CHARACTER LARGE OBJECT", "national character large object"),
    ("id_national_character_varying", "NATIONAL CHARACTER VARYING", "national character varying"),
    ("id_national_character", "NATIONAL CHARACTER", "NC"),
    ("id_nchar_large_object", "NCHAR LARGE OBJECT", "nchar large object"),
    ("id_nchar_varying", "NCHAR VARYING", "nchar varying"),
    ("id_real", "REAL", 123.456),
    # ("id_set", "SET", "value1,value2"),
    ("id_signed", "SIGNED", -123),
    ("id_single", "SINGLE", 123.4),
    ("id_smallint_signed", "SMALLINT SIGNED", -32768),
    ("id_smallint_unsigned", "SMALLINT UNSIGNED", 65535),
    ("id_smallint", "SMALLINT", 32767),
    ("id_string", "STRING", "string value"),
    ("id_text", "TEXT", "text value"),
    ("id_time", "TIME", "12:34:56"),
    # ("id_tinyblob", "TINYBLOB", b"tinyblob"),
    ("id_tinyint_signed", "TINYINT SIGNED", -128),
    # ("id_tinyint_unsigned", "TINYINT UNSIGNED", 255),
    ("id_tinyint", "TINYINT", 127),
    ("id_tinytext", "TINYTEXT", "tiny text"),
    ("id_uint16", "UINT16", 65535),
    ("id_uint32", "UINT32", 4294967295),
    ("id_uint64", "UINT64", 18446744073709551615),
    ("id_uint8", "UINT8", 255),
    ("id_unsigned", "UNSIGNED", 123),
    ("id_uuid", "UUID", "550e8400-e29b-41d4-a716-446655440000"),
    ("id_varchar", "VARCHAR", "varchar value"),
]


@pytest.mark.parametrize("column_schema", column_schema)
def test_clickhouse_destination_basic_types(testcase_parameters, config, syslog_ng, column_schema, clickhouse_server, clickhouse_client):
    table_name = "test_table_1"
    column_name = column_schema[0]
    column_type = column_schema[1]
    columnt_test_value = column_schema[2]
    clickhouse_config_schema = f'"{column_name}" "{column_type}" => ${column_name}'
    filterx_code = f"${column_name} = json($MSG).{column_name};"

    print(f"Testing Clickhouse destination with column: {column_name}, type: {column_type}, value: {columnt_test_value}")
    print(f"Clickhouse config schema: {clickhouse_config_schema}")
    print(f"Filterx code: {filterx_code}")

    generator_source = config.create_example_msg_generator_source(
        num=1,
        template=config.stringify("{'ID': 1, '%s': '%s'}" % (column_name, columnt_test_value)),
    )
    filterx = config.create_filterx(f"$ID = json($MSG).ID; {filterx_code}")
    clickhouse_destination = config.create_clickhouse_destination(
        database="default",
        table=table_name,
        user="default",
        schema=f'"ID" "Integer" => "$ID", {clickhouse_config_schema}',
    )
    config.create_logpath(statements=[generator_source, filterx, clickhouse_destination])

    copy_shared_file(testcase_parameters, "clickhouse.proto")
    clickhouse_server.start()
    clickhouse_client.aaa(table_name, [(column_name, column_type)])
    # clickhouse_client.delete_table(table_name)
    # clickhouse_client.create_table(table_name, [("id_message", "STRING")], table_name)

    syslog_ng.start(config)
    time.sleep(1)

    clickhouse_client.run_query(f"SELECT * FROM {table_name}")
    clickhouse_client.run_query(f"desc {table_name} format jsoneachrow ;")


def test_clickhouse_destination_nested_types(testcase_parameters, config, syslog_ng, clickhouse_server, clickhouse_client):
    table_name = "test_table_2"
    # column_name = "AAAA"
    # column_type = "VVVVV"
    # columnt_test_value = "CDDDDDDDD"
    # clickhouse_config_schema = f'"{column_name}" "{column_type}" => ${column_name}'

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
        proto_var="$protobuf_message",
    )
    config.create_logpath(statements=[generator_source, filterx, clickhouse_destination])

    copy_shared_file(testcase_parameters, "clickhouse_server_config.xml")
    copy_shared_file(testcase_parameters, "clickhouse_users.xml")
    copy_shared_file(testcase_parameters, "clickhouse.proto")
    clickhouse_server.start()
    clickhouse_client.aaa(
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
    time.sleep(1)
    syslog_ng.stop()

    clickhouse_client.run_query(f"SELECT * FROM {table_name}")
    # clickhouse_client.run_query(f"desc {table_name} format jsoneachrow ;")
