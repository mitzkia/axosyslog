#############################################################################
# Copyright (c) 2015-2016 Balabit
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

from .completerlang import CompleterLang
from .commandlinelexer import CommandLineLexer
from .getoptlexer import GetoptLexer


class DebugLang(CompleterLang):
    # we only need to list commands we want to automatically complete arguments.
    # Commands that have no arguments don't need to be listed as they wouldn't really
    # have rules anyway.
    _known_commands = (
        "print",
        "display",
    )
    _aliases = {
        'p': 'print',
    }
    tokens = [
        "COMMAND_PRINT", "COMMAND_DISPLAY",
        "COMMAND",
        "ARG",
    ]

    def p_statement(self, p):
        '''statement : print_command
                    | display_command
                    | generic_command'''

    def p_args(self, p):
        '''args : ARG args
               | '''

    def p_print_command(self, p):
        '''print_command : COMMAND_PRINT template'''

    def p_display_command(self, p):
        '''display_command : COMMAND_DISPLAY template'''

    def p_generic_command(self, p):
        '''generic_command : COMMAND args'''

    def p_template(self, p):
        '''template : ARG'''

    def _construct_lexer(self):
        return GetoptLexer(CommandLineLexer(),
                           known_commands=self._known_commands,
                           aliases=self._aliases)
