#!/usr/bin/env python
#############################################################################
# Copyright (c) 2023 Balazs Scheidler <balazs.scheidler@axoflow.com>
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
import pytest


test_parameters = [
    ("$(format-json test.*)\n", """{"test":{"key2":"value2","key1":"value1"}}\n"""),
    # transformations
    ("$(format-json test.* --add-prefix foo.)\n", """{"foo":{"test":{"key2":"value2","key1":"value1"}}}\n"""),
    ("$(format-json test.* --replace-prefix test=foobar)\n", """{"foobar":{"key2":"value2","key1":"value1"}}\n"""),
    ("$(format-json test.* --shift-levels 1)\n", """{"key2":"value2","key1":"value1"}\n"""),
    ("$(format-json test.* --shift 2)\n", """{"st":{"key2":"value2","key1":"value1"}}\n"""),
    ("$(format-json test.* --upper)\n", """{"TEST":{"KEY2":"value2","KEY1":"value1"}}\n"""),
    ("$(format-json MESSAGE --lower)\n", """{"message":"-- Generated message. --"}\n"""),
]


@pytest.mark.parametrize(
    "template, expected_value", test_parameters,
    ids=list(map(lambda x: x[0], test_parameters)),
)
def atest_value_pairs(config, syslog_ng, template, expected_value):

    generator_source = config.create_example_msg_generator_source(num=1, values="test.key1 => value1 test.key2 => value2")
    file_destination = config.create_file_destination(file_name="output.log", template=config.stringify(template))

    config.create_logpath(statements=[generator_source, file_destination])
    syslog_ng.start(config)
    log = file_destination.read_log()
    assert log == expected_value




import string
from hypothesis import given, settings, HealthCheck, strategies as st

def gen_number():
    return st.integers(min_value=0, max_value=200)

# @pytest.mark.example_msg_generator_source
# @pytest.mark.file_destination
# @pytest.mark.values
@given(gen_number())
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=2, database=None, deadline=None)
def test_values_int(config, syslog_ng, integers):
    syslog_ng.stop()
    config.reset()

    config.update_global_options(stats="level(5)")
    generator_source = config.create_example_msg_generator_source(num=1, values='"values.int" => int(%d)' % integers)
    file_destination = config.create_file_destination(file_name="output.log", template='"${values.int}\n"')
    config.create_logpath(statements=[generator_source, file_destination])

    syslog_ng.start(config)
    assert file_destination.get_stats()["processed"] == 1
    assert str(integers) in file_destination.read_until_logs(["%d" % integers])[0]


def gen_list():
    twoints = st.tuples(st.integers(), st.text(alphabet=string.ascii_letters + string.digits, min_size=1), st.floats(min_value=1, max_value=10, allow_nan=False, allow_infinity=False, allow_subnormal=False))
    return st.lists(twoints)

@given(gen_list())
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=10, database=None, deadline=None)
def test_values_list(config, syslog_ng, input_list):
    syslog_ng.stop()
    config.reset()
    print(input_list)
    q = ""
    for i in input_list:
        for a in i:
            # print(type(a))
            if isinstance(a, str):
                q += "'%s', " % str(a)
            else:
                q += "%s, " % a
    # print(q)
    # assert True
    config.update_global_options(stats="level(5)")
    generator_source = config.create_example_msg_generator_source(num=1, values='"values.list" => list(%s)' % q)
    file_destination = config.create_file_destination(file_name="output.log", template='"${values.list}\n"')
    config.create_logpath(statements=[generator_source, file_destination])

    syslog_ng.start(config)
    assert file_destination.get_stats()["processed"] == 1
    assert str(input_list) in file_destination.read_until_logs(["%s" % input_list])[0]
