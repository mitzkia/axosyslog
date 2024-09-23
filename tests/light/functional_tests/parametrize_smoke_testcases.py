#!/usr/bin/env python
#############################################################################
# Copyright (c) 2022 Andras Mitzki <mitzkia@gmail.com>
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
from pathlib import Path

import axosyslog_cfg_helper
from axosyslog_cfg_helper.driver_db import DriverDB





# @settings(suppress_health_check=[HealthCheck.return_value], max_examples=5, database=None, deadline=None)
def generate_options_and_values_for_driver(expected_context, expected_driver, string):
    option_value_type_to_value_map = {
        "<float>": -12.34,
        "<number>": -12,
        "KW_SYSLOG": "syslog",
        "<string-or-number>": "QQQQ",
        "check-hostname": "check-hostname",
        "<nonnegative-integer>": 100,
        "<nonnegative-float>": 12.34,
        "<positive-integer>": 6789,
        "<string-list>": "aaa bbb ccc",
        "<string>": "'%s'" % string,
        "<template-content>": "'$MSG\n'",
        "<yesno>": "yes",
        "<empty>": "",
        "persist-only": "persist-only",
        "<string> => <template-content>": '"HOST" => "host$(iterate $(+ 1 $_) 0)"',
        "<string> <arrow> <template-content>": '"HOST" => "host$(iterate $(+ 1 $_) 0)"',
        "<string> => <string>": "AAA => BBB",
        "<string> => <number>": "AAA => 1",
    }

    option_name_to_value_map = {
        "default-facility": "'kern'",
        "default-level": "'emerg'",
        "default-priority": "'emerg'",
        "default-severity": "'emerg'",
        "encoding": "'WINDOWS-1251'",
        "flags": "'no-parse'",
        "format": "'syslog'",
        "setup": "'pwd'",
        "startup": "'pwd'",
    }

    tc_type = "all_options"
    options = []
    a_options = {}

    print("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF: %s" % option_value_type_to_value_map)

    def generate_option_properties_for_driver(driver_db, expected_context, expected_driver):
        contexts = list(driver_db.contexts)
        # print(contexts)
        source_drivers = []
        destination_drivers = []
        parser_drivers = []
        filter_drivers = []
        option_value_types = []
        # print("111111111111111111-1: %s" % dir(driver_db))
        # print("111111111111111111: %s" % driver_db.get_drivers_in_context("source"))
        for r in contexts:
            for a in driver_db.get_drivers_in_context(r):
                # print("EEEEEEEEEEEEEEEEEEEEEEEE: %s" % a)
                # print("EEEEEEEEEEEEEEEEEEEEEEEE-2: %s" % type(a))
                # print("EEEEEEEEEEEEEEEEEEEEEEEE-3: %s" % dir(a))
                # print("EEEEEEEEEEEEEEEEEEEEEEEE-4: %s" % vars(a))
                # print("EEEEEEEEEEEEEEEEEEEEEEEE-4: %s" % a.context)
                # print("EEEEEEEEEEEEEEEEEEEEEEEE-5: %s" % a.name)
                source_drivers.append(a.name)
                # print("EEEEEEEEEEEEEEEEEEEEEEEE-6: %s" % a.options)
                for b in a.options:
                    for c in b.params:
                        if c not in option_value_types:
                            option_value_types.append(c)

        print("BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB: %s" % option_value_types)
        print("BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB-2: %s" % len(option_value_types))
        # import sys
        # sys.exit(1)
        for option in driver_db.get_driver(expected_context, expected_driver).to_dict()["options"]:
            yield driver_db.get_driver(expected_context, expected_driver).to_dict()["options"][option]["name"], driver_db.get_driver(expected_context, expected_driver).to_dict()["options"][option]["params"], None

    def get_option_value(option_name, option_type):
        if option_type == "":
            return ""
        if option_name in option_name_to_value_map:
            return option_name_to_value_map[option_name]
        else:
            return option_value_type_to_value_map[option_type]

    def build_option_block(block_names, option_and_value):
        option_block = {}

        def update_option_block(option_block, subkey):
            option_block.update({subkey: {}})
            return option_block[subkey]

        for index, block_name in enumerate(block_names, start=1):
            if option_block == {}:
                working_option_block = update_option_block(option_block, block_name)
            else:
                working_option_block = update_option_block(working_option_block, block_name)
            if index == len(block_names):
                working_option_block.update(option_and_value)
        return option_block


    db_file = Path(axosyslog_cfg_helper.__path__[0], "axosyslog-cfg-helper.db")
    with db_file.open("r") as file:
        driver_db = DriverDB.load(file)

    for option_names, option_types, block_names in generate_option_properties_for_driver(driver_db, expected_context, expected_driver):
        if option_names == None:
            continue
        for option_name in option_names.split("/"):
            if not block_names:
                for option_type in option_types:
                    if len(option_type) != 1:
                        option_type = [" ".join(option_type)]
                    if tc_type == "per_option":
                        options.append({option_name: get_option_value(option_name, option_type[0])})
                    elif tc_type == "all_options":
                        a_options.update({option_name: get_option_value(option_name, option_type[0])})
                    else:
                        raise Exception("nincs ilyen lehetoseg")
            else:
                print("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF2")
                import sys
                sys.exit(1)
                # result_option_block = build_option_block(block_names, {option_name: get_option_value(option_name, option_type)})
                # options.append(result_option_block)

    if tc_type == "per_option":
        # print("GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG1")
        return options
    elif tc_type == "all_options":
        # print("GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG2")
        # print(a_options)
        return [a_options]
    else:
        print("OOOOOOOOOOOOOOOOOOOOOOOOOOOOOO")
        return None


def generate_id_name(param):
    def stringify_parameter(param):
        return repr(param).replace("{", "").replace("}", "").replace("'", "").replace(":", "").replace('"', "").replace(" ", "_")
    return stringify_parameter(param)
