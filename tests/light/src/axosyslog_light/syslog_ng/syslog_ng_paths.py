#!/usr/bin/env python
#############################################################################
# Copyright (c) 2015-2018 Balabit
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

from axosyslog_light.common.random_id import get_unique_id


class SyslogNgPaths(object):
    def __init__(self, testcase_parameters):
        self.__testcase_parameters = testcase_parameters
        self.__instance_name = None
        self.__syslog_ng_paths = {}

    def set_syslog_ng_paths(self, instance_name):
        if self.__instance_name is not None:
            raise Exception("Instance already configured")
        self.__instance_name = instance_name
        self.__syslog_ng_paths = {
            "file_paths": {
                "config_path": Path("syslog_ng_{}.conf".format(instance_name)),
                "persist_path": Path("syslog_ng_{}.persist".format(instance_name)),
                "pid_path": Path("syslog_ng_{}.pid".format(instance_name)),
                "control_socket_path": Path("syslog_ng_{}.ctl".format(instance_name)),
                "stderr": Path("syslog_ng_{}_stderr".format(instance_name)),
                "stdout": Path("syslog_ng_{}_stdout".format(instance_name)),
                "syntax_only_stderr": Path("syslog_ng_{}_syntax_only_stderr".format(instance_name)),
                "syntax_only_stdout": Path("syslog_ng_{}_syntax_only_stdout".format(instance_name)),
            },
        }

        try:
            install_dir = self.__testcase_parameters.get_install_dir()
            self.__syslog_ng_paths.update(
                {
                    "dirs": {"install_dir": install_dir},
                    "binary_file_paths": {
                        "slogkey": Path(install_dir, "bin", "slogkey"),
                        "slogverify": Path(install_dir, "bin", "slogverify"),
                        "syslog_ng_binary": Path(install_dir, "sbin", "syslog-ng"),
                        "syslog_ng_ctl": Path(install_dir, "sbin", "syslog-ng-ctl"),
                        "loggen": Path(install_dir, "bin", "loggen"),
                    },
                },
            )
        except KeyError:
            pass

        return self

    def get_instance_name(self):
        return self.__instance_name

    def get_install_dir(self):
        return self.__syslog_ng_paths["dirs"]["install_dir"]

    def get_config_path(self):
        return self.__syslog_ng_paths["file_paths"]["config_path"]

    def get_persist_path(self):
        return self.__syslog_ng_paths["file_paths"]["persist_path"]

    def get_pid_path(self):
        return self.__syslog_ng_paths["file_paths"]["pid_path"]

    def get_control_socket_path(self):
        return self.__syslog_ng_paths["file_paths"]["control_socket_path"]

    def get_stderr_path(self):
        return self.__syslog_ng_paths["file_paths"]["stderr"]

    def get_stderr_path_with_postfix(self, postfix):
        return Path("{}_{}".format(self.__syslog_ng_paths["file_paths"]["stderr"], postfix))

    def get_stdout_path(self):
        return self.__syslog_ng_paths["file_paths"]["stdout"]

    def get_stdout_path_with_postfix(self, postfix):
        return Path("{}_{}".format(self.__syslog_ng_paths["file_paths"]["stdout"], postfix))

    def get_syntax_only_stderr_path(self):
        return self.__syslog_ng_paths["file_paths"]["syntax_only_stderr"]

    def get_syntax_only_stdout_path(self):
        return self.__syslog_ng_paths["file_paths"]["syntax_only_stdout"]

    def get_syslog_ng_bin(self):
        return self.__syslog_ng_paths["binary_file_paths"]["syslog_ng_binary"]

    def get_slogkey_bin(self):
        return self.__syslog_ng_paths["binary_file_paths"]["slogkey"]

    def get_slogverify_bin(self):
        return self.__syslog_ng_paths["binary_file_paths"]["slogverify"]

    def get_syslog_ng_ctl_bin(self):
        return self.__syslog_ng_paths["binary_file_paths"]["syslog_ng_ctl"]

    def get_loggen_bin(self):
        return self.__syslog_ng_paths["binary_file_paths"]["loggen"]

    def register_external_tool_output_path(self, external_tool):
        self.__syslog_ng_paths['file_paths'].update(
            {
                external_tool: Path("{}_{}.log".format(external_tool, get_unique_id())),
            },
        )

    def get_external_tool_output_path(self, external_tool):
        return self.__syslog_ng_paths['file_paths'][external_tool]
