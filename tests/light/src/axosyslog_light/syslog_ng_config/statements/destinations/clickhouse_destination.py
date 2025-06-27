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
# from pathlib import Path
# from axosyslog_light.driver_io.file.file_io import FileIO
from axosyslog_light.syslog_ng_config.statements.destinations.destination_driver import DestinationDriver
from axosyslog_light.syslog_ng_ctl.legacy_stats_handler import LegacyStatsHandler
from axosyslog_light.syslog_ng_ctl.prometheus_stats_handler import PrometheusStatsHandler


class ClickhouseDestination(DestinationDriver):
    def __init__(
        self,
        stats_handler: LegacyStatsHandler,
        prometheus_stats_handler: PrometheusStatsHandler,
        **options,
    ) -> None:
        self.driver_name = "clickhouse"
        super(ClickhouseDestination, self).__init__(stats_handler, prometheus_stats_handler, None, options)

    # def get_path(self):
    #     return self.path

    # def read_log(self):
    #     return self.read_logs(1)[0]

    # def read_logs(self, counter):
    #     return self.io.read_number_of_messages(counter)

    # def read_until_logs(self, logs):
    #     return self.io.read_until_messages(logs)

    # def close_file(self):
    #     self.io.close_readable_file()
