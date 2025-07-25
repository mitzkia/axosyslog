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
import typing
from pathlib import Path

from axosyslog_light.executors.command_executor import CommandExecutor
from axosyslog_light.syslog_ng_ctl.syslog_ng_ctl_executor import SyslogNgCtlExecutor


class SyslogNgCtlLocalExecutor(SyslogNgCtlExecutor):
    def __init__(
        self,
        syslog_ng_ctl_binary_path: Path,
        syslog_ng_control_socket_path: Path,
    ) -> None:
        self.__syslog_ng_ctl_binary_path = syslog_ng_ctl_binary_path
        self.__syslog_ng_control_socket_path = syslog_ng_control_socket_path
        self.__command_executor = CommandExecutor()

    def run_command(
        self,
        instance_name: str,
        command_short_name: str,
        command: typing.List[str],
    ) -> typing.Dict[str, typing.Any]:
        ctl_command = [self.__syslog_ng_ctl_binary_path]
        ctl_command += command
        ctl_command.append("--control={}".format(self.__syslog_ng_control_socket_path))

        return self.__command_executor.run(
            command=ctl_command,
            stdout_path=self.construct_std_file_path(instance_name, command_short_name, "stdout"),
            stderr_path=self.construct_std_file_path(instance_name, command_short_name, "stderr"),
        )
