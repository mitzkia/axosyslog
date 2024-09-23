#!/usr/bin/env python
#############################################################################
# Copyright (c) 2023 Attila Szakacs
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
from typing import Dict
from typing import NamedTuple
from typing import Optional

import prometheus_client.parser
from prometheus_client.samples import Sample

import src.testcase_parameters.testcase_parameters as tc_parameters
from src.syslog_ng_ctl.syslog_ng_ctl import SyslogNgCtl

__all__ = ["PrometheusStatsHandler", "MetricFilter", "Sample"]


class MetricFilter(NamedTuple):
    name: str
    labels: Optional[Dict[str, str]] = None


class PrometheusStatsHandler(object):
    def __init__(self, metric_filters):
        self.__metric_filters = metric_filters
        self.__syslog_ng_ctl = SyslogNgCtl(tc_parameters.INSTANCE_PATH)

    def __filter_raw_samples(self, raw_samples):
        samples = []

        for metric_family in prometheus_client.parser.text_string_to_metric_families(raw_samples):
            for sample in metric_family.samples:
                for metric_filter in self.__metric_filters:
                    if metric_filter.name == sample.name and metric_filter.labels.items() <= sample.labels.items():
                        samples.append(sample)

        return samples

    def get_samples(self):
        if len(self.__metric_filters) == 0:
            return []

        ctl_output = self.__syslog_ng_ctl.stats_prometheus()
        print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
        print(ctl_output)
        if ctl_output["exit_code"] != 0:
            return []

        return self.__filter_raw_samples(ctl_output["stdout"])
