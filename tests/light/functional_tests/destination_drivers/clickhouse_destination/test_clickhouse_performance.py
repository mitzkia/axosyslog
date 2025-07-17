import datetime
import logging
import time

from axosyslog_light.common.blocking import wait_until_true_custom
from axosyslog_light.helpers.loggen.loggen import LoggenStartParams

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

clickhouse_valid_options = {
    "database": "default",
    "table": "test_table",
    "user": "default",
    "password": "'password'",
    "schema": '"message" "String" => "$MESSAGE"',
    "workers": 1,
    "batch_lines": 50000,
    "batch_timeout": 50000,
    "disk-buffer": {
        # "disk-buf-size": 10000000,  # 10 MB
        "mem-buf-length": 100000,      # 1000 messages in memory
        "mem-buf-size": 1000000,     # 1 MB in memory
    },
}


def test_clickhouse_destination_perf_generic_padd(config, syslog_ng, clickhouse_server, clickhouse_client, port_allocator, loggen):
    network_source = config.create_network_source(ip="localhost", port=port_allocator(), transport="tcp", log_iw_size=10000, log_fetch_limit=1000)
    clickhouse_destination = config.create_clickhouse_destination(**clickhouse_valid_options)
    config.create_logpath(statements=[network_source, clickhouse_destination])

    MSG_COUNTER = 2000000

    clickhouse_server.start()
    clickhouse_client.create_table("test_table", [("message", "String")])

    syslog_ng.start_params.trace = False
    syslog_ng.start_params.debug = False
    syslog_ng.start_params.verbose = False

    syslog_ng.start(config)
    time.sleep(1)

    loggen.start(
        LoggenStartParams(
            target=network_source.options["ip"],
            port=network_source.options["port"],
            inet=True,
            perf=True,
            active_connections=1,
            number=MSG_COUNTER,
        ),
    )

    logger.info("AAA-1: actual datetime: %s" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    assert wait_until_true_custom(lambda: loggen.get_sent_message_count() == MSG_COUNTER, timeout=180)
    logger.info("AAA-2: actual datetime: %s" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    assert wait_until_true_custom(lambda: clickhouse_destination.get_stats()["written"] == MSG_COUNTER, timeout=180)
    logger.info("AAA-3: actual datetime: %s" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    assert clickhouse_client.run_query("SELECT COUNT(*) FROM test_table;") == MSG_COUNTER, f"Expected {MSG_COUNTER} messages"
    logger.info("AAA-4: actual datetime: %s" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    try:
        syslog_ng.stop()
    except Exception as e:
        logger.error(f"Error stopping syslog-ng: {e}")
        pass


def test_clickhouse_destination_perf_complex_filterx(config, syslog_ng, clickhouse_server, clickhouse_client, port_allocator, loggen):
    network_source = config.create_network_source(ip="localhost", port=port_allocator(), transport="tcp", log_iw_size=10000, log_fetch_limit=1000)
    clickhouse_destination = config.create_clickhouse_destination(**clickhouse_valid_options)
    config.create_logpath(statements=[network_source, clickhouse_destination])

    MSG_COUNTER = 2000000

    clickhouse_server.start()
    clickhouse_client.create_table("test_table", [("message", "String")])

    syslog_ng.start_params.trace = False
    syslog_ng.start_params.debug = False
    syslog_ng.start_params.verbose = False

    syslog_ng.start(config)
    time.sleep(1)

    loggen.start(
        LoggenStartParams(
            target=network_source.options["ip"],
            port=network_source.options["port"],
            inet=True,
            perf=True,
            active_connections=1,
            number=MSG_COUNTER,
        ),
    )

    logger.info("AAA-1: actual datetime: %s" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    assert wait_until_true_custom(lambda: loggen.get_sent_message_count() == MSG_COUNTER, timeout=180)
    logger.info("AAA-2: actual datetime: %s" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    assert wait_until_true_custom(lambda: clickhouse_destination.get_stats()["written"] == MSG_COUNTER, timeout=180)
    logger.info("AAA-3: actual datetime: %s" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    assert clickhouse_client.run_query("SELECT COUNT(*) FROM test_table;") == MSG_COUNTER, f"Expected {MSG_COUNTER} messages"
    logger.info("AAA-4: actual datetime: %s" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    try:
        syslog_ng.stop()
    except Exception as e:
        logger.error(f"Error stopping syslog-ng: {e}")
        pass
