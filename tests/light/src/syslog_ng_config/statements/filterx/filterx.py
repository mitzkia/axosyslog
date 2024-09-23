#!/usr/bin/env python
from src.syslog_ng_ctl.driver_stats_handler import DriverStatsHandler


class Filterx(object):
    group_type = "filterx"

    def __init__(self, driver_name, filterx_content):
        self.driver_name = driver_name
        self.driver_raw_content = filterx_content
        self.stats_handler = DriverStatsHandler(group_type=self.group_type, driver_name=self.driver_name)

    def get_stats(self):
        return self.stats_handler.get_stats()

    def get_query(self):
        return self.stats_handler.get_query()
