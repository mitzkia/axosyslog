def test_a(config, syslog_ng):
    file_source = config.create_file_source(file_name="input.log")
    file_destination = config.create_file_destination(file_name="output.log")
    config.create_logpath(statements=[file_source, file_destination])

    file_source.write_log("<38>Feb 11 21:27:22 testhost testprogram[9999]: test message\n", 2)
    syslog_ng.start(config)

    config.create_raw_logpath("""dasldk as;dlkas
    dsla;kd;aslkda;skdas
    das
    """)

    syslog_ng.stop()
    syslog_ng.start(config)

    assert True
