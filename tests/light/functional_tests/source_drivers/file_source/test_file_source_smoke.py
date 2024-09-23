# #!/usr/bin/env python
# #############################################################################
# # Copyright (c) 2022 Andras Mitzki <mitzkia@gmail.com>
# #
# # This program is free software; you can redistribute it and/or modify it
# # under the terms of the GNU General Public License version 2 as published
# # by the Free Software Foundation, or (at your option) any later version.
# #
# # This program is distributed in the hope that it will be useful,
# # but WITHOUT ANY WARRANTY; without even the implied warranty of
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# # GNU General Public License for more details.
# #
# # You should have received a copy of the GNU General Public License
# # along with this program; if not, write to the Free Software
# # Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# #
# # As an additional exemption you are allowed to compile & link against the
# # OpenSSL libraries as published by the OpenSSL project. See the file
# # COPYING for details.
# #
# #############################################################################
import pytest
from functional_tests.parametrize_smoke_testcases import generate_id_name
from functional_tests.parametrize_smoke_testcases import generate_options_and_values_for_driver
input_log = "<38>Feb 11 21:27:22 testhost testprogram[9999]: test message\n"
@pytest.mark.parametrize("option_and_value", generate_options_and_values_for_driver("source", "file"), ids=generate_id_name)
def test_file_source_smoke(config, syslog_ng, option_and_value):
    file_source = config.create_file_source(file_name="input.log", **option_and_value)
    file_destination = config.create_file_destination(file_name="output.log")
    config.create_logpath(statements=[file_source, file_destination])
    file_source.write_log(input_log, 1)
    syslog_ng.start(config)
    file_source.write_log(input_log, 1)
    syslog_ng.reload(config)
    assert file_destination.read_log() != ""



MESSAGES = [
    "<38>Feb 11 21:27:22 testhost testprogram[9999]: normal legacy BSD\n",
    "<38>Feb 11 21:27:22 testhost testprogram[9999]: normal legacy BSD too max message size (65535 byte) " + "PADD"*65535 + "\n",
    "<38>Feb 11 21:27:22 testhost testprogram[9999]: normal legacy BSD too max message size (65535 byte) " + "PADD"*65535 + "OVER MAX size" + "\n",
    "<38>Feb 11 21:27:22 testhost testprogram[9999]: normal legacy BSD and UTF8 chars ÁRVÍZTŰRŐÜTVEFÚRÓGÉP - Y݌Ӝ򄞍o빕ꨱ𲀋񟵃wQ򝂒ܲE妐ʜÅʉ񌔞ݦ=曺懛ỿ񹮮箬𘙪Gǆ񇢞􈚢󘰼񨰟ꕄ1䤂₇Ⱦᗒ_É%𡳯򂀵;蜉ԁ瑾ιᇍ❱𓫩󋘖䟣b򷒱dÃח8ѩ�덿*ۮɑk񻙋Ø񺩗뫑㖤QҼ󸷬ͭ𗩱Ꭼ$ޓ򘛶𺢐r媶ᴯ𨳍}ɽՏM騡y묱ʟC¸F򣶤z뫞ᨫ[󾉕󒃮4ڨ륾U24ߏ𿻘x֨𡔥󽍕Ҏ㖇D򎊋ҽǎ绸1݀󟎝砘캹ի񞪏b8ହSBw叄g񏓟ڕ𚉀>쎥􇹧惗nꈃ*խG誡DS∹Г򿃁ѓ\n",
    "<38>Feb 11 21:27:22 testhost testprogram[9999]: normal legacy BSD " + "\x00 \escaoe \\escape \n",
    
]
