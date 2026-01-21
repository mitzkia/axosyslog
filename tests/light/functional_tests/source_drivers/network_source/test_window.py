#!/usr/bin/env python
#############################################################################
# Copyright (c) 2026 Axoflow
# Copyright (c) 2026 Andras Mitzki <andras.mitzki@axoflow.com>
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
from axosyslog_light.common.blocking import wait_until_true
from axosyslog_light.helpers.loggen.loggen import LoggenStartParams
from axosyslog_light.syslog_ng_ctl.prometheus_stats_handler import MetricFilter


def send_messages(loggen, network_source, active_connections, message_counter_per_connection):
    for i in range(active_connections):
        loggen.start(
            LoggenStartParams(
                target=network_source.options["ip"],
                port=network_source.options["port"],
                inet=True,
                active_connections=1,
                number=message_counter_per_connection,
            ),
        )
        wait_until_true(lambda: loggen.get_sent_message_count() == message_counter_per_connection)
        loggen.stop()


def set_default_config_for_initial_window(config, port_allocator):
    config.update_global_options(stats_level=5)
    network_source = config.create_network_source(ip="localhost", port=port_allocator())
    network_destination = config.create_network_destination(ip="localhost", port=port_allocator(), time_reopen=1)
    config.create_logpath(statements=[network_source, network_destination], flags="flow-control")
    return config, network_source, network_destination


def check_statistics(network_destination, expected_stats):
    for stat_name, expected_value in expected_stats.items():
        assert wait_until_true(lambda: stat_name in network_destination.get_stats() and network_destination.get_stats()[stat_name] == expected_value), "Expected stat {} not found in stats".format(stat_name)


def get_metric(config, metric_name):
    return config.get_prometheus_samples([MetricFilter(metric_name, {})])[0].value


def check_prometheus_metrics(config, expected_metrics):
    for metric_name, expected_value in expected_metrics.items():
        actual_value = get_metric(config, metric_name)
        assert actual_value == expected_value, f"Metric {metric_name} expected: {expected_value}, actual: {actual_value}"


def fill_up_initial_window_buffer_and_check(config, network_source, network_destination, loggen, syslog_ng):
    send_messages(loggen, network_source, active_connections=DEFAULT_MAX_CONNECTIONS, message_counter_per_connection=DEFAULT_INITIAL_WINDOW_SIZE)

    check_statistics(
        network_destination, {
            "processed": INPUT_WINDOW_CAPACITY,
            "dropped": 0,
            "queued": INPUT_WINDOW_CAPACITY,
            "written": 0,
        },
    )
    check_prometheus_metrics(config, {"syslogng_input_window_available": 0, "syslogng_input_window_capacity": DEFAULT_INITIAL_WINDOW_SIZE})
    assert syslog_ng.count_message_in_console_log("Source has been suspended") == DEFAULT_MAX_CONNECTIONS


def send_additional_one_message_and_check(network_source, loggen, syslog_ng):
    assert not syslog_ng.is_message_in_console_log("Number of allowed concurrent connections reached, rejecting connection")
    send_messages(loggen, network_source, active_connections=1, message_counter_per_connection=1)
    assert syslog_ng.is_message_in_console_log("Number of allowed concurrent connections reached, rejecting connection")


def start_destination_and_check(config, network_destination):
    network_destination.start_listener()
    assert network_destination.read_logs(counter=1000)
    check_statistics(
        network_destination, {
            "processed": INPUT_WINDOW_CAPACITY,
            "dropped": 0,
            "queued": 0,
            "written": INPUT_WINDOW_CAPACITY,
        },
    )
    check_prometheus_metrics(config, {"syslogng_input_window_available": INPUT_WINDOW_CAPACITY, "syslogng_input_window_capacity": INPUT_WINDOW_CAPACITY})


DEFAULT_LOG_IW_SIZE = 1000
DEFAULT_MAX_CONNECTIONS = 10
DEFAULT_INITIAL_WINDOW_SIZE = int(DEFAULT_LOG_IW_SIZE / DEFAULT_MAX_CONNECTIONS)
INPUT_WINDOW_CAPACITY = DEFAULT_INITIAL_WINDOW_SIZE * DEFAULT_MAX_CONNECTIONS


def test_default_initial_window(config, syslog_ng, port_allocator, loggen):
    config, network_source, network_destination = set_default_config_for_initial_window(config, port_allocator)
    syslog_ng.start(config)

    fill_up_initial_window_buffer_and_check(config, network_source, network_destination, loggen, syslog_ng)
    send_additional_one_message_and_check(network_source, loggen, syslog_ng)
    start_destination_and_check(config, network_destination)

    syslog_ng.stop()


def set_default_config_for_dynamic_window(config, port_allocator):
    config.update_global_options(stats_level=5)
    network_source = config.create_network_source(ip="localhost", port=port_allocator(), log_iw_size=1, max_connections=10, dynamic_window_size=200, dynamic_window_realloc_ticks=1)
    network_destination = config.create_network_destination(ip="localhost", port=port_allocator(), time_reopen=1)
    config.create_logpath(statements=[network_source, network_destination], flags="flow-control")
    return config, network_source, network_destination


def fill_up_all_window_buffer_for_first_connection_and_check(loggen, network_source, config):
    send_messages(loggen, network_source, active_connections=1, message_counter_per_connection=300)
    check_prometheus_metrics(config, {"syslogng_input_window_available": 0, "syslogng_input_window_capacity": DEFAULT_INITIAL_WINDOW_SIZE})


def check_rebalance_with_sending_new_logs_with_second_connection_and_check(loggen):
    pass


def test_default_dynamic_window(config, syslog_ng, port_allocator, loggen):
    config, network_source, network_destination = set_default_config_for_dynamic_window(config, port_allocator)
    syslog_ng.start(config)
    fill_up_all_window_buffer_for_first_connection_and_check(loggen, network_source, config)
    check_rebalance_with_sending_new_logs_with_second_connection_and_check(loggen)

    syslog_ng.stop()
