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
import random


def random_key(keys):
    return random.choice(keys)


def random_syslog_prefix():
    return random.choice(
        [
            # "<13>1 2019-01-18T11:07:53.520Z 192.168.1.1 ",
            "Jan 18 11:07:53 myhostname myprog[12345]: ",
            "<13>Jan 18 11:07:53 192.168.1.1 myprog[12345]: ",
        ],
    )


def generate_csv_message(target_length=512):
    syslog_prefix = random_syslog_prefix()
    csv_header_list = [
        "1,2014/01/28 01:28:35,007200001056,TRAFFIC,end,",
        "1,2025/03/14 16:28:52,111111111111111,CONFIG,0,",
        "1,2012/10/30 09:46:17,01606001116,THREAT,url,",
        "1,2025/04/02 17:55:34,1111111111111111111,HIPMATCH,0,",
        "1,2021/01/23 00:45:03,012001003714,SYSTEM,userid,",
        "1,2025/03/28 05:40:45,000000000000,USERID,login,",
    ]
    csv_part_list = [
        ":::::RSA",
        "",
        "0",
        "0x0",
        "0x8000000000000000",
        "1.1.1.1",
        "1.1.1.2",
        "1.1.1.3",
        "1",
        "10.1.1.1",
        "1111",
        "111111111111111",
        "2021/01/22 18:00:10",
        "2025-04-02T15:56:19.287+00:00",
        "4",
        "able-to-transfer-file",
        "browser-based",
        "browser-based",
        "encrypted-tunnel",
        "general-internet",
        "has-known-vulnerability",
        "Intermediate CA",
        "internet-utility",
        "N/A",
        "networking",
        "no",
        "None",
        "PADD PADD PADD PADD PADD PADD PADD PADD PADD",
        "pervasive-use",
        "tunnel-other-application",
        "url.com",
        "used-by-malware",
        "web-browsing",
    ]

    csv_header = random_key(csv_header_list)
    msg_content = ""
    while len(syslog_prefix + csv_header + msg_content) < target_length:
        msg_content += random_key(csv_part_list) + ","

    full_message = (syslog_prefix + csv_header + msg_content).strip()
    return full_message[:target_length] + "\n"


def generate_sample_log(input_msg_type, msg_size):
    if input_msg_type == "csv":
        return generate_csv_message(msg_size)
    else:
        raise ValueError(f"Unsupported input message type: {input_msg_type}")
