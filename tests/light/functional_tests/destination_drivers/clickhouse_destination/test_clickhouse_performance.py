import logging

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
}


def test_clickhouse_destination_perf(config, syslog_ng, clickhouse_server, clickhouse_client, port_allocator, loggen):

    network_source = config.create_network_source(
        ip="localhost",
        port=port_allocator(),
        transport="tcp",
    )
    # generator_source = config.create_example_msg_generator_source(num=1, template=f'"{custom_input_msg}"')
    clickhouse_destination = config.create_clickhouse_destination(**clickhouse_valid_options)
    config.create_logpath(statements=[network_source, clickhouse_destination])

    clickhouse_server.start()
    clickhouse_client.create_table("test_table", [("message", "String")])

    # syslog_ng.start_params.stderr = False
    syslog_ng.start_params.trace = False
    # syslog_ng.start_params.verbose = False

    syslog_ng.start(config)
    loggen.start(
        LoggenStartParams(
            target=network_source.options["ip"],
            port=network_source.options["port"],
            inet=True,
            # rate=100000,
            perf=True,
            active_connections=1,
            number=2000000,
        ),
    )

    wait_until_true_custom(lambda: loggen.get_sent_message_count() == 2000000, timeout=180)

    import time
    time.sleep(20)  # Allow some time for the message to be processed
    # assert clickhouse_destination.get_stats()["written"] >= 1

    aaa = clickhouse_client.run_query("SELECT COUNT(*) FROM test_table;")
    logger.info(f"Query result: {aaa}")
    assert aaa == 2000000, f"Expected 2000000 messages, but got {aaa}"
    # db_logs = clickhouse_destination.read_logs()
    # logger.info(db_logs)  # For debugging purposes, can be removed later
    # assert len(db_logs) == 100000
    try:
        syslog_ng.stop()
    except Exception as e:
        logger.error(f"Error stopping syslog-ng: {e}")
        pass
