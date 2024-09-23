import json
import pytest



@pytest.mark.parametrize("source_driver_name", ["file", "example_msg_generator", "network"])
def test_source_driver_input_generic(config, syslog_ng, source_driver_name):
    input_message = "test message for driver {}\n".format(source_driver_name)
    config.update_global_options(stats_level=5)
    create_source_driver = getattr(config, 'create_{}_source'.format(source_driver_name))
    if source_driver_name == "example_msg_generator":
        source_driver = create_source_driver(template="'{}'".format(input_message))
    else:
        source_driver = create_source_driver()
    file_destination = config.create_file_destination(file_name="output_destination_for_{}.log".format(source_driver_name))
    config.create_logpath(statements=[source_driver, file_destination])
    
    syslog_ng.start(config)

    input_message = "test message for driver {}\n".format(source_driver_name)
    source_driver.write_log(input_message)
    assert input_message in file_destination.read_log()

    if source_driver_name == "network":
        expected_stats_keys = sorted(['connections', 'msg_size_avg', 'msg_size_max', 'eps_since_start', 'eps_last_1h', 'eps_last_24h', 'processed', 'stamp', 'free_window', 'full_window'])
    elif source_driver_name == "example_msg_generator":
        expected_stats_keys = sorted(['stamp', 'processed', 'free_window', 'full_window'])
    elif source_driver_name == "file":
        expected_stats_keys = sorted(['msg_size_max', 'stamp', 'eps_since_start', 'eps_last_1h', 'eps_last_24h', 'msg_size_avg', 'processed', 'free_window', 'full_window'])
    assert sorted(list(source_driver.get_stats().keys())) == expected_stats_keys
    assert source_driver.get_stats()['processed'] == 1

    syslog_ng.stop()


EEE = {
    "AMPM": "PM",
    "BSDTAG": "6E",
    "C_AMPM": "AM",
    "C_DATE": "Sep 23 04:21:39",
    "C_DAY": "23",
    "C_FULLDATE": "2024 Sep 23 04:21:39",
    "C_HOUR": "04",
    "C_HOUR12": "04",
    "C_ISODATE": "2024-09-23T04:21:39+00:00",
    "C_ISOWEEK": "39",
    "C_MIN": "21",
    "C_MONTH_ABBREV": "Sep",
    "C_MONTH_NAME": "September",
    "C_MONTH_WEEK": "4",
    "C_MONTH": "09",
    "C_MSEC": "951",
    "C_SEC": "39",
    "C_STAMP": "Sep 23 04:21:39",
    "C_TZ": "+00:00",
    "C_TZOFFSET": "+00:00",
    "C_UNIXTIME": "1727065299",
    "C_USEC": "951082",
    "C_WEEK_DAY_ABBREV": "Mon",
    "C_WEEK_DAY_NAME": "Monday",
    "C_WEEK_DAY": "2",
    "C_WEEK": "39",
    "C_WEEKDAY": "Mon",
    "C_YEAR_DAY": "267",
    "C_YEAR": "2024",
    "DATE": "Feb 11 21:27:22",
    "DAY": "11",
    "DESTIP": "127.0.0.1",
    "DESTPORT": 0,
    "FACILITY_NUM": 4,
    "FACILITY": "auth",
    "FILE_NAME": "input.log",
    "FULLDATE": "2024 Feb 11 21:27:22",
    "HOST_FROM": "DESKTOP-0E9OKG3",
    "HOST": "DESKTOP-0E9OKG3",
    "HOSTID": "3184b4c2",
    "HOUR": "21",
    "HOUR12": "09",
    "IP_PROTO": 0,
    "ISODATE": "2024-02-11T21:27:22+00:00",
    "ISOWEEK": "06",
    "LEGACY_MSGHDR": "testprogram[9999]: ",
    "LEVEL_NUM": 6,
    "LEVEL": "info",
    "LOGHOST": "DESKTOP-0E9OKG3",
    "MESSAGE": "test message",
    "MIN": "27",
    "MONTH_ABBREV": "Feb",
    "MONTH_NAME": "February",
    "MONTH_WEEK": "1",
    "MONTH": "02",
    "MSEC": "000",
    "MSG": "test message",
    "MSGFORMAT": "syslog:rfc3164",
    "MSGHDR": "testprogram[9999]: ",
    "P_AMPM": "AM",
    "P_DATE": "Sep 23 04:21:39",
    "P_DAY": "23",
    "P_FULLDATE": "2024 Sep 23 04:21:39",
    "P_HOUR": "04",
    "P_HOUR12": "04",
    "P_ISODATE": "2024-09-23T04:21:39+00:00",
    "P_ISOWEEK": "39",
    "P_MIN": "21",
    "P_MONTH_ABBREV": "Sep",
    "P_MONTH_NAME": "September",
    "P_MONTH_WEEK": "4",
    "P_MONTH": "09",
    "P_MSEC": "951",
    "P_SEC": "39",
    "P_STAMP": "Sep 23 04:21:39",
    "P_TZ": "+00:00",
    "P_TZOFFSET": "+00:00",
    "P_UNIXTIME": "1727065299",
    "P_USEC": "951082",
    "P_WEEK_DAY_ABBREV": "Mon",
    "P_WEEK_DAY_NAME": "Monday",
    "P_WEEK_DAY": "2",
    "P_WEEK": "39",
    "P_WEEKDAY": "Mon",
    "P_YEAR_DAY": "267",
    "P_YEAR": "2024",
    "PID": "9999",
    "PRI": "38",
    "PRIORITY": "info",
    "PROGRAM": "testprogram",
    "PROTO": 0,
    "R_AMPM": "AM",
    "R_DATE": "Sep 23 04:21:39",
    "R_DAY": "23",
    "R_FULLDATE": "2024 Sep 23 04:21:39",
    "R_HOUR": "04",
    "R_HOUR12": "04",
    "R_ISODATE": "2024-09-23T04:21:39+00:00",
    "R_ISOWEEK": "39",
    "R_MIN": "21",
    "R_MONTH_ABBREV": "Sep",
    "R_MONTH_NAME": "September",
    "R_MONTH_WEEK": "4",
    "R_MONTH": "09",
    "R_MSEC": "950",
    "R_SEC": "39",
    "R_STAMP": "Sep 23 04:21:39",
    "R_TZ": "+00:00",
    "R_TZOFFSET": "+00:00",
    "R_UNIXTIME": "1727065299",
    "R_USEC": "950480",
    "R_WEEK_DAY_ABBREV": "Mon",
    "R_WEEK_DAY_NAME": "Monday",
    "R_WEEK_DAY": "2",
    "R_WEEK": "39",
    "R_WEEKDAY": "Mon",
    "R_YEAR_DAY": "267",
    "R_YEAR": "2024",
    "RAWMSG_SIZE": 60,
    "RCPTID": "1",
    "RUNID": "1",
    "S_AMPM": "PM",
    "S_DATE": "Feb 11 21:27:22",
    "S_DAY": "11",
    "S_FULLDATE": "2024 Feb 11 21:27:22",
    "S_HOUR": "21",
    "S_HOUR12": "09",
    "S_ISODATE": "2024-02-11T21:27:22+00:00",
    "S_ISOWEEK": "06",
    "S_MIN": "27",
    "S_MONTH_ABBREV": "Feb",
    "S_MONTH_NAME": "February",
    "S_MONTH_WEEK": "1",
    "S_MONTH": "02",
    "S_MSEC": "000",
    "S_SEC": "22",
    "S_STAMP": "Feb 11 21:27:22",
    "S_TZ": "+00:00",
    "S_TZOFFSET": "+00:00",
    "S_UNIXTIME": "1707686842",
    "S_USEC": "000000",
    "S_WEEK_DAY_ABBREV": "Sun",
    "S_WEEK_DAY_NAME": "Sunday",
    "S_WEEK_DAY": "1",
    "S_WEEK": "06",
    "S_WEEKDAY": "Sun",
    "S_YEAR_DAY": "042",
    "S_YEAR": "2024",
    "SDATA": '[meta sequenceId="1"]',
    "SEC": "22",
    "SEQNUM": "1",
    "SEVERITY_NUM": 6,
    "SEVERITY": "info",
    "SOURCE": "source_193098457507015667442758709755903361700",
    "SOURCEIP": "127.0.0.1",
    "STAMP": "Feb 11 21:27:22",
    "SYSUPTIME": "213",
    "TAG": "26",
    "TAGS": "['.source.source_193098457507015667442758709755903361700']",
    "TRANSPORT": "local+file",
    "TZ": "+00:00",
    "TZOFFSET": "+00:00",
    "UNIQID": "3184b4c2@0000000000000001",
    "UNIXTIME": "1707686842",
    "USEC": "000000",
    "WEEK_DAY_ABBREV": "Sun",
    "WEEK_DAY_NAME": "Sunday",
    "WEEK_DAY": "1",
    "WEEK": "06",
    "WEEKDAY": "Sun",
    "YEAR": "2024",
    "YEAR_DAY": "042",
}

@pytest.mark.parametrize("source_driver_name", ["file", "network", "example_msg_generator"])
def test_message_fields_for_source_drivers_generic(config, syslog_ng, source_driver_name, log_message, bsd_formatter):
    input_message = bsd_formatter.format_message(log_message)
    config.update_global_options(stats_level=5)
    create_source_driver = getattr(config, 'create_{}_source'.format(source_driver_name))
    if source_driver_name == "example_msg_generator":
        source_driver = create_source_driver(template="'{}'".format(input_message))
    else:
        source_driver = create_source_driver()
    file_destination = config.create_file_destination(file_name="output_destination_for_{}.log".format(source_driver_name), template='"$(format-json --scope everything)\n"')
    config.create_logpath(statements=[source_driver, file_destination])
    
    syslog_ng.start(config)
    source_driver.write_log(input_message)
    for message_field, field_value in json.loads(file_destination.read_log()).items():
        if message_field == "TRANSPORT" and source_driver_name == "file":
            assert field_value == "local+file"
        elif message_field == "TRANSPORT" and source_driver_name == "network":
            assert field_value == "bsdsyslog+tcp"
        elif message_field == "PROTO" and source_driver_name == "network":
            assert field_value == 6
        elif message_field == "IP_PROTO" and source_driver_name == "network":
            assert field_value == 4
        elif message_field == "DESTPORT" and source_driver_name == "network":
            assert field_value == 30001
        elif message_field in ["HOST_FROM", "HOST"] and source_driver_name == "network":
            assert field_value == "localhost"
        elif message_field in ["TAG"] and source_driver_name == "example_msg_generator":
            assert field_value == "0d"
        elif message_field in ["SEVERITY_NUM"] and source_driver_name == "example_msg_generator":
            assert field_value == 5
        elif message_field in ["SEVERITY"] and source_driver_name == "example_msg_generator":
            assert field_value == 'notice'
        elif message_field in ["PRIORITY"] and source_driver_name == "example_msg_generator":
            assert field_value == 'notice'
        elif message_field in ["PRI"] and source_driver_name == "example_msg_generator":
            assert field_value == '13'
        elif message_field in ["MSG"] and source_driver_name == "example_msg_generator":
            assert field_value == '<38>Feb 11 21:27:22 testhost testprogram[9999]: test message\n'
        elif message_field in ["RAWMSG_SIZE"] and source_driver_name == "example_msg_generator":
            assert field_value == 0
        elif message_field in ["YEAR_DAY", "WEEK_DAY_NAME", "WEEK_DAY_ABBREV", "WEEK_DAY", "WEEKDAY", "WEEK", "USEC", "UNIXTIME", "STAMP", "SEC", "MSEC", "MONTH_WEEK", "MONTH_NAME", "MONTH_ABBREV", "MONTH", "MIN"] and source_driver_name == "example_msg_generator":
            pass
        elif  message_field not in ["UNIQID", "TAGS", "SYSUPTIME", "SOURCE", "HOSTID"] and \
            not message_field.startswith("R_") and \
            not message_field.startswith("P_") and \
            not message_field.startswith("C_") and \
            not message_field.startswith("S_"):
                assert field_value == EEE[message_field]