#!/usr/bin/env python
#############################################################################
# Copyright (c) 2025 Axoflow
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
# import datetime
import logging
import time

import pytest
from axosyslog_light.common.blocking import wait_until_true_custom
from axosyslog_light.helpers.loggen.loggen import LoggenStartParams
# import uuid
# from axosyslog_light.common.file import copy_shared_file


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def send_msg(loggen, network_source, msg_counter, input_msg):
    input_message_file_name = "input_message.txt"
    with open(input_message_file_name, "w") as f:
        for i in range(msg_counter):
            f.write(input_msg)
    loggen.start(
        LoggenStartParams(
            target=network_source.options["ip"],
            port=network_source.options["port"],
            inet=True,
            perf=True,
            active_connections=1,
            number=msg_counter,
            read_file=input_message_file_name,
            dont_parse=True,
            loop_reading=False,
        ),
    )
    assert wait_until_true_custom(lambda: loggen.get_sent_message_count() == msg_counter, timeout=300)


def start_syslog_ng(syslog_ng, config):
    syslog_ng.start_params.trace = False
    syslog_ng.start_params.debug = False
    syslog_ng.start_params.verbose = False
    syslog_ng.start(config)
    time.sleep(0.5)


# MSG origin: https://www.ibm.com/docs/en/dsm?topic=fireeye-sample-event-message
sample_cef_message = '<149>Jul 23 18:54:24 fireeye.mps.test cef[5159]: CEF:0|fireeye|HX|4.8.0|IOC Hit Found|IOC Hit Found|10|rt=Jul 23 2019 16:54:24 UTC dvchost=fireeye.mps.test categoryDeviceGroup=/IDS categoryDeviceType=Forensic Investigation categoryObject=/Host cs1Label=Host Agent Cert Hash cs1=fwvqcmXUHVcbm4AFK01cim dst=192.168.1.172 dmac=00-00-5e-00-53-00 dhost=test-host1 dntdom=test deviceCustomDate1Label=Agent Last Audit deviceCustomDate1=Jul 23 2019 16:54:22 UTC cs2Label=FireEye Agent Version cs2=29.7.0 cs5Label=Target GMT Offset cs5=+PT2H cs6Label=Target OS cs6=Windows 10 Pro 17134 externalId=17688554 start=Jul 23 2019 16:53:18 UTC categoryOutcome=/Success categorySignificance=/Compromise categoryBehavior=/Found cs7Label=Resolution cs7=ALERT cs8Label=Alert Types cs8=exc act=Detection IOC Hit msg=Host test-host1 IOC compromise alert categoryTupleDescription=A Detection IOC found a compromise indication. cs4Label=IOC Name cs4=SVCHOST SUSPICIOUS PARENT PROCESS\n'
# MSG origin: https://www.ibm.com/docs/en/dsm?topic=series-palo-alto-pa-sample-event-message
sample_csv_message = sample_leef_message = '<180>May  6 16:43:53 paloalto.paseries.test leef[9876]: LEEF:1.0|Palo Alto Networks|PAN-OS Syslog Integration|8.1.6|trojan/PDF.gen.eiez(268198686)|ReceiveTime=2019/05/06 16:43:53|SerialNumber=001801010877|cat=THREAT|Subtype=virus|devTime=May 06 2019 11:13:53 GMT|src=10.2.75.41|dst=192.168.178.180|srcPostNAT=192.168.68.141|dstPostNAT=192.168.178.180|RuleName=Test-1|usrName=qradar\\user1|SourceUser=qradar\\user1|DestinationUser=|Application=web-browsing|VirtualSystem=vsys1|SourceZone=INSIDE-ZN|DestinationZone=OUTSIDE-ZN|IngressInterface=ethernet1/1|EgressInterface=ethernet1/3|LogForwardingProfile=testForwarder|SessionID=3012|RepeatCount=1|srcPort=63508|dstPort=80|srcPostNATPort=31539|dstPostNATPort=80|Flags=0x406000|proto=tcp|action=alert|Miscellaneous=\"qradar.example.test/du/uploads/08052018_UG_FAQ.pdf\"|ThreatID=trojan/PDF.gen.eiez(268198686)|URLCategory=educational-institutions|sev=3|Severity=medium|Direction=server-to-client|sequence=486021038|ActionFlags=0xa000000000000000|SourceLocation=10.0.0.0-10.255.255.255|DestinationLocation=testPlace|ContentType=|PCAP_ID=0|FileDigest=|Cloud=|URLIndex=5|RequestMethod=|Subject=|DeviceGroupHierarchyL1=12|DeviceGroupHierarchyL2=0|DeviceGroupHierarchyL3=0|DeviceGroupHierarchyL4=0|vSrcName=|DeviceName=testName|SrcUUID=|DstUUID=|TunnelID=0|MonitorTag=|ParentSessionID=0|ParentStartTime=|TunnelType=N/A|ThreatCategory=pdf|ContentVer=Antivirus-2969-3479\n'
# MSG origin: https://www.ibm.com/docs/en/dsm?topic=mwsel-microsoft-windows-security-event-log-sample-event-messages
sample_windows_eventlog_xml_message = sample_xml_message = "<180>May  6 16:43:53 testhost.test xml[9876]: <Event xmlns='http://schemas.microsoft.com/win/2004/08/events/event'><System><Provider Name='Microsoft-Windows-Security-Auditing' Guid='{22222222-2222-2222-2222-222222222222}'/><EventID>5061</EventID><Version>0</Version><Level>0</Level><Task>12290</Task><Opcode>0</Opcode><Keywords>0x8020000000000000</Keywords><TimeCreated SystemTime='2019-05-07T17:53:30.064817200Z'/><EventRecordID>291478</EventRecordID><Correlation ActivityID='{33333333-3333-3333-3333-333333333333}'/><Execution ProcessID='700' ThreadID='1176'/><Channel>Security</Channel><Computer>computer_name</Computer><Security/></System><EventData><Data Name='SubjectUserSid'>subject_user_sid</Data><Data Name='SubjectUserName'>subject_user_name</Data><Data Name='SubjectDomainName'>WORKGROUP</Data><Data Name='SubjectLogonId'>0x3e7</Data><Data Name='ProviderName'>Microsoft Software Key Storage Provider</Data><Data Name='AlgorithmName'>RSA</Data><Data Name='KeyName'>{44444444-4444-4444-4444-444444444444}</Data><Data Name='KeyType'>%%2499</Data><Data Name='Operation'>%%2480</Data><Data Name='ReturnCode'>0x0</Data></EventData></Event>\n"
# MSG origin: https://www.ibm.com/docs/en/dsm?topic=i-sample-event-message
sample_kv_message = '<176>Apr 24 15:31:58 ibm.i.test kv[9876]: LEEF:1.0|Raz-Lee iSecurity|Firewall|1.0|GRE7860|usrName=USERNAME devTime=2019-04-24-15.31.58.000  devTimeFormat=yyyy-MM-dd-HH.mm.ss.SSS source=172.16.1.1    sev=10  jobName=948290/QUSER/QRWTSRVR pgmName=*NONE    pgmLib=*NONE    entryType=36/A  entryDesc=DRDA Distributed Relational DB access   Action_allowed=1   Src_user_before_Pre-chk=USERNAME   Source_system=SYSTEM1  Decision_level=USSRV  Authority_set_to_user=USERNAME    Server_Id=36\n'
# MSG origin: https://www.ibm.com/docs/en/dsm?topic=auditing-kubernetes-sample-event-message
sample_json_message = '<133>Oct 21 10:37:55 test.example.com k8s-audit: {"kind":"Event","apiVersion":"audit.k8s.io/v1","level":"RequestResponse","auditID":"d30b40b8-4f6a-4219-9828-a7f732518541","stage":"ResponseComplete","requestURI":"/api/v1/namespaces/default/endpoints/kubernetes","verb":"get","user":{"username":"system:apiserver","uid":"0f440c21-a1c6-4ec3-84a4-50cd5dee2eb7","groups":["system:masters"]},"sourceIPs":["::1"],"userAgent":"kube-apiserver/v1.15.2 (linux/amd64) kubernetes/f627830","objectRef":{"resource":"endpoints","namespace":"default","name":"kubernetes","apiVersion":"v1"},"responseStatus":{"metadata":{},"code":200},"responseObject":{"kind":"Endpoints","apiVersion":"v1","metadata":{"name":"kubernetes","namespace":"default","selfLink":"/api/v1/namespaces/default/endpoints/kubernetes","uid":"1104e39a-46d2-4c35-92d2-5206dc6be4d2","resourceVersion":"156","creationTimestamp":"2019-10-21T13:18:48Z"},"subsets":[{"addresses":[{"ip":"192.0.2.0/24"}],"ports":[{"name":"https","port":6443,"protocol":"TCP"}]}]},"requestReceivedTimestamp":"2019-10-21T14:37:53.788926Z","stageTimestamp":"2019-10-21T14:37:53.789945Z"}\n'
parsed_cef_message = 'Jul 23 18:54:24 localhost cef[5159]: {"version":"0","device_vendor":"fireeye","device_product":"HX","device_version":"4.8.0","device_event_class_id":"IOC Hit Found","name":"IOC Hit Found","agent_severity":"10","rt":"Jul 23 2019 16:54:24 UTC","dvchost":"fireeye.mps.test","categoryDeviceGroup":"/IDS","categoryDeviceType":"Forensic Investigation","categoryObject":"/Host","cs1Label":"Host Agent Cert Hash","cs1":"fwvqcmXUHVcbm4AFK01cim","dst":"192.168.1.172","dmac":"00-00-5e-00-53-00","dhost":"test-host1","dntdom":"test","deviceCustomDate1Label":"Agent Last Audit","deviceCustomDate1":"Jul 23 2019 16:54:22 UTC","cs2Label":"FireEye Agent Version","cs2":"29.7.0","cs5Label":"Target GMT Offset","cs5":"+PT2H","cs6Label":"Target OS","cs6":"Windows 10 Pro 17134","externalId":"17688554","start":"Jul 23 2019 16:53:18 UTC","categoryOutcome":"/Success","categorySignificance":"/Compromise","categoryBehavior":"/Found","cs7Label":"Resolution","cs7":"ALERT","cs8Label":"Alert Types","cs8":"exc","act":"Detection IOC Hit","msg":"Host test-host1 IOC compromise alert","categoryTupleDescription":"A Detection IOC found a compromise indication.","cs4Label":"IOC Name","cs4":"SVCHOST SUSPICIOUS PARENT PROCESS"}\n'
parsed_leef_message = 'May  6 16:43:53 localhost leef[9876]: {"version":"1.0","vendor":"Palo Alto Networks","product_name":"PAN-OS Syslog Integration","product_version":"8.1.6","event_id":"trojan/PDF.gen.eiez(268198686)","ReceiveTime":"2019/05/06 16:43:53|SerialNumber=001801010877|cat=THREAT|Subtype=virus|devTime=May 06 2019 11:13:53 GMT|src=10.2.75.41|dst=192.168.178.180|srcPostNAT=192.168.68.141|dstPostNAT=192.168.178.180|RuleName=Test-1|usrName=qradar_user1|SourceUser=qradar_user1|DestinationUser=|Application=web-browsing|VirtualSystem=vsys1|SourceZone=INSIDE-ZN|DestinationZone=OUTSIDE-ZN|IngressInterface=ethernet1/1|EgressInterface=ethernet1/3|LogForwardingProfile=testForwarder|SessionID=3012|RepeatCount=1|srcPort=63508|dstPort=80|srcPostNATPort=31539|dstPostNATPort=80|Flags=0x406000|proto=tcp|action=alert|Miscellaneous=\\"qradar.example.test/du/uploads/08052018_UG_FAQ.pdf\\"|ThreatID=trojan/PDF.gen.eiez(268198686)|URLCategory=educational-institutions|sev=3|Severity=medium|Direction=server-to-client|sequence=486021038|ActionFlags=0xa000000000000000|SourceLocation=10.0.0.0-10.255.255.255|DestinationLocation=testPlace|ContentType=|PCAP_ID=0|FileDigest=|Cloud=|URLIndex=5|RequestMethod=|Subject=|DeviceGroupHierarchyL1=12|DeviceGroupHierarchyL2=0|DeviceGroupHierarchyL3=0|DeviceGroupHierarchyL4=0|vSrcName=|DeviceName=testName|SrcUUID=|DstUUID=|TunnelID=0|MonitorTag=|ParentSessionID=0|ParentStartTime=|TunnelType=N/A|ThreatCategory=pdf|ContentVer=Antivirus-2969-3479"}\n'

# MSG origin: https://www.ibm.com/docs/en/dsm?topic=auditing-kubernetes-sample-event-message
legacy_bsd_json_256 = '<133>Oct 21 10:37:55 test.example.com k8s-audit: {"kind":"Event","apiVersion":"audit.k8s.io/v1","level":"RequestResponse","auditID":"d30b40b8-4f6a-4219-9828-a7f732518541","stage":"ResponseComplete","requestURI":"/api/v1/namespaces/default/endpoints/kubernetes"}\n'
legacy_bsd_json_512 = '<133>Oct 21 10:37:55 test.example.com k8s-audit: {"kind":"Event","apiVersion":"audit.k8s.io/v1","level":"RequestResponse","auditID":"d30b40b8-4f6a-4219-9828-a7f732518541","stage":"ResponseComplete","requestURI":"/api/v1/namespaces/default/endpoints/kubernetes","verb":"get","user":{"username":"system:apiserver","uid":"0f440c21-a1c6-4ec3-84a4-50cd5dee2eb7","groups":["system:masters"]},"sourceIPs":["::1"],"userAgent":"kube-apiserver/v1.15.2 (linux/amd64) kubernetes/f627830","objectRef":{"resource":"endpoints",}}\n'
legacy_bsd_json_756 = '<133>Oct 21 10:37:55 test.example.com k8s-audit: {"kind":"Event","apiVersion":"audit.k8s.io/v1","level":"RequestResponse","auditID":"d30b40b8-4f6a-4219-9828-a7f732518541","stage":"ResponseComplete","requestURI":"/api/v1/namespaces/default/endpoints/kubernetes","verb":"get","user":{"username":"system:apiserver","uid":"0f440c21-a1c6-4ec3-84a4-50cd5dee2eb7","groups":["system:masters"]},"sourceIPs":["::1"],"userAgent":"kube-apiserver/v1.15.2 (linux/amd64) kubernetes/f627830","objectRef":{"resource":"endpoints","namespace":"default","name":"kubernetes","apiVersion":"v1"},"responseStatus":{"metadata":{},"code":200},"responseObject":{"kind":"Endpoints","apiVersion":"v1","metadata":{"name":"kubernetes","namespace":"default","selfLink":"/api/v1/namespaces/default/endpoints/kubernetes"}}}\n'
legacy_bsd_json = '<133>Oct 21 10:37:55 test.example.com k8s-audit: {"kind":"Event","apiVersion":"audit.k8s.io/v1","level":"RequestResponse","auditID":"d30b40b8-4f6a-4219-9828-a7f732518541","stage":"ResponseComplete","requestURI":"/api/v1/namespaces/default/endpoints/kubernetes","verb":"get","user":{"username":"system:apiserver","uid":"0f440c21-a1c6-4ec3-84a4-50cd5dee2eb7","groups":["system:masters"]},"sourceIPs":["::1"],"userAgent":"kube-apiserver/v1.15.2 (linux/amd64) kubernetes/f627830","objectRef":{"resource":"endpoints","namespace":"default","name":"kubernetes","apiVersion":"v1"},"responseStatus":{"metadata":{},"code":200},"responseObject":{"kind":"Endpoints","apiVersion":"v1","metadata":{"name":"kubernetes","namespace":"default","selfLink":"/api/v1/namespaces/default/endpoints/kubernetes","uid":"1104e39a-46d2-4c35-92d2-5206dc6be4d2","resourceVersion":"156","creationTimestamp":"2019-10-21T13:18:48Z"},"subsets":[{"addresses":[{"ip":"192.0.2.0/24"}],"ports":[{"name":"https","port":6443,"protocol":"TCP"}]}]},"requestReceivedTimestamp":"2019-10-21T14:37:53.788926Z","stageTimestamp":"2019-10-21T14:37:53.789945Z","annotations":{"authorization.k8s.io/decision":"allow","authorization.k8s.io/reason":""}}\n'
perf_tc_variants = [
    # msg_counter, input_msg, modifier, filterx_rule
    # (10, sample_csv_message[:256] + "\n", "", "", "file-dst"),
    # (10, sample_csv_message[:512] + "\n", "", "", "file-dst"),
    # (10, sample_csv_message[:756] + "\n", "", "", "file-dst"),
    (3000000, sample_csv_message, "", "", ""),

    # csv-parser + filterx
    (3000000, sample_csv_message, "csv-parser-delimiter", "filterx-from-csv-parser-input", ""),

    # Filterx builtin simple functions
    (3000000, sample_csv_message, "", "filterx-builtin-simple-functions", ""),

    # Filterx parse functions
    (3000000, sample_cef_message, "", "filterx-parse-cef", ""),
    (3000000, sample_csv_message, "", "filterx-parse-csv", ""),   # final MSG output type: dict
    (3000000, sample_kv_message, "", "filterx-parse-kv", ""),
    (3000000, sample_leef_message, "", "filterx-parse-leef", ""),
    (3000000, sample_xml_message, "", "filterx-parse-xml", ""),
    (3000000, sample_windows_eventlog_xml_message, "", "filterx-parse-windows-eventlog-xml", ""),

    # Filterx format functions
    (3000000, parsed_cef_message, "", "filterx-format-cef", ""),
    (3000000, sample_json_message, "", "filterx-format-csv", ""),
    (3000000, sample_json_message, "", "filterx-format-kv", ""),
    (3000000, parsed_leef_message, "", "filterx-format-leef", ""),
    (3000000, sample_json_message, "", "filterx-format-xml", ""),
    (3000000, sample_json_message, "", "filterx-format-windows-eventlog-xml", ""),

    # Filterx parse and format functions
    (3000000, sample_csv_message, "", "filterx-with-parse-csv-and-format-json", ""),   # final MSG output type: string

]


def build_modifier(modifier, config, config_statements, input_msg):
    if modifier == "csv-parser-delimiter":
        modifier = config.create_csv_parser(prefix=config.stringify("prefix."), delimiters=config.stringify("|"))

    if modifier == "csv-parser-columns":
        number_of_delimiters = input_msg.count("|")
        column_names = ", ".join(f"'{i + 1}'" for i in range(number_of_delimiters + 1))
        modifier = config.create_csv_parser(prefix=config.stringify("prefix."), columns=column_names, delimiters=config.stringify("|"))

    config_statements.append(modifier)
    return config_statements


def build_filterx_rule(filterx_rule, config, config_statements, input_msg):
    if filterx_rule == "filterx-builtin-simple-functions":
        filterx_expr = "$log = {'data': {}};"
        filterx_expr += "$log.data['bool'] = bool('$MSG');"
        filterx_expr += "$log.data['bytes'] = bytes('$MSG');"
        filterx_expr += "$log.data['datetime'] = datetime('$MSG');"
        filterx_expr += "$log.data['dedup_metrics_labels'] = dedup_metrics_labels(metrics_labels());"
        filterx_expr += "$log.data['dict'] = dict({'msg': $MSG});"
        filterx_expr += "$log.data['double'] = double('$R_SEC');"
        filterx_expr += "$log.data['format_json'] = format_json('$MSG');"
        filterx_expr += "$log.data['get_sdata'] = get_sdata();"
        filterx_expr += "$log.data['has_sdata'] = has_sdata();"
        filterx_expr += "$log.data['int'] = int('$R_SEC');"
        filterx_expr += "$log.data['isodate'] = isodate('$MSG');"
        filterx_expr += "$log.data['json_array'] = json_array(list([$MSG]));"
        filterx_expr += "$log.data['json'] = json({'msg': $MSG});"
        filterx_expr += "$log.data['len'] = len('$MSG');"
        # filterx_expr += "$log.data['list'] = list([$log]);"  ## crash-r okoz
        filterx_expr += "$log.data['list'] = list([$MSG]);"
        # filterx_expr += "$log.data['load_vars'] = load_vars('$MSG');" ## crash-t okoz
        filterx_expr += "$log.data['load_vars'] = load_vars($log);"
        filterx_expr += "$log.data['lower'] = lower('$MSG');"
        filterx_expr += "$log.data['metrics_labels'] = metrics_labels();"
        filterx_expr += "$log.data['parse_json'] = parse_json(string({'msg':$MSG}));"
        filterx_expr += "$log.data['protobuf'] = protobuf(bytes('$MSG'));"
        filterx_expr += "$log.data['repr'] = repr('$MSG');"
        filterx_expr += "$log.data['str_replace'] = str_replace($MSG, 'cat', 'dog');"
        filterx_expr += "$log.data['string'] = string('$MSG');"
        filterx_expr += "$log.data['upper'] = upper('$MSG');"
        filterx_expr += "$MESSAGE = $log;"

    if filterx_rule == "filterx-parse-cef":
        filterx_expr = "cef = parse_cef($MSG);\n"
        filterx_expr += "$MESSAGE = cef;"

    if filterx_rule == "filterx-parse-csv":
        column_names = []
        number_of_delimiters = input_msg.count("|")
        for i in range(number_of_delimiters + 1):
            column_names.append(f"column_{i}")
        filterx_expr = f"defined_columns = {column_names};\n"
        filterx_expr += "$log = parse_csv($MSG, delimiter='|', columns=defined_columns);\n"
        filterx_expr += "$MESSAGE = $log;"

    if filterx_rule == "filterx-parse-kv":
        filterx_expr = "kv = parse_kv($MSG);\n"
        filterx_expr += "$MESSAGE = kv;"

    if filterx_rule == "filterx-parse-leef":
        filterx_expr = "leef = parse_leef($MSG);\n"
        filterx_expr += "$MESSAGE = leef;"

    if filterx_rule == "filterx-parse-windows-eventlog-xml":
        filterx_expr = "xml = parse_windows_eventlog_xml($MSG);\n"
        filterx_expr += "$MESSAGE = xml;"

    if filterx_rule == "filterx-parse-xml":
        filterx_expr = "xml = parse_xml($MSG);\n"
        filterx_expr += "$MESSAGE = xml;"

    if filterx_rule == "filterx-format-cef":
        filterx_expr = "cef = format_cef(json($MSG));\n"
        filterx_expr += "$MESSAGE = cef;"

    if filterx_rule == "filterx-format-csv":
        filterx_expr = "csv = format_csv(json($MSG));\n"
        filterx_expr += "$MESSAGE = csv;"

    if filterx_rule == "filterx-format-kv":
        filterx_expr = "kv = format_kv(json($MSG));\n"
        filterx_expr += "$MESSAGE = kv;"

    if filterx_rule == "filterx-format-leef":
        filterx_expr = "leef = format_leef(json($MSG));\n"
        filterx_expr += "$MESSAGE = leef;"

    if filterx_rule == "filterx-format-windows-eventlog-xml":
        filterx_expr = "xml = format_windows_eventlog_xml(json($MSG));\n"
        filterx_expr += "$MESSAGE = xml;"

    if filterx_rule == "filterx-format-xml":
        filterx_expr = "xml = format_xml(json($MSG));\n"
        filterx_expr += "$MESSAGE = xml;"

    if filterx_rule == "filterx-from-csv-parser-input":
        filterx_expr = "$log = {};\n"
        number_of_delimiters = input_msg.count("|")
        for i in range(number_of_delimiters + 1):
            filterx_expr += f'$log["{i + 1}"] = ".${i}";\n'
        filterx_expr += '$MESSAGE = {"message": $log};\n'

    if filterx_rule == "filterx-with-parse-csv-and-format-json":
        column_names = []
        number_of_delimiters = input_msg.count("|")
        for i in range(number_of_delimiters + 1):
            column_names.append(f"column_{i}")
        filterx_expr = f"defined_columns = {column_names};"
        filterx_expr += "$log = parse_csv($MSG, delimiter='|', columns=defined_columns);"
        filterx_expr += "$MESSAGE = format_json($log);"

    filterx = config.create_filterx(filterx_expr)
    config_statements.append(filterx)
    return config_statements


@pytest.mark.parametrize("msg_counter, input_msg, modifier, filterx_rule, destination", perf_tc_variants, ids=range(len(perf_tc_variants)))
def test_clickhouse_destination_perf2(request, testcase_parameters, config, syslog_ng, clickhouse_server, port_allocator, loggen, msg_counter, input_msg, modifier, filterx_rule, destination):
    config_statements = []
    network_source = config.create_network_source(ip="localhost", port=port_allocator(), transport="tcp", log_iw_size=100000, log_fetch_limit=10000)
    config_statements.append(network_source)

    if modifier:
        config_statements = build_modifier(modifier, config, config_statements, input_msg)

    if filterx_rule:
        config_statements = build_filterx_rule(filterx_rule, config, config_statements, input_msg)

    if destination == "file-dst":
        file_destination = config.create_file_destination(file_name="output.log")
        config_statements.append(file_destination)

    config.create_logpath(statements=config_statements)

    start_syslog_ng(syslog_ng, config)
    send_msg(loggen, network_source, msg_counter, input_msg)
    time.sleep(1)
    syslog_ng.stop()

    logger.info("Loggen stats: %s", loggen.get_loggen_stats().msg_per_second)
