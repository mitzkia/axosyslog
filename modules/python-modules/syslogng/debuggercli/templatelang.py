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

from __future__ import print_function, absolute_import
from .completerlang import CompleterLang
from .templatelexer import TemplateLexer


class TemplateLang(CompleterLang):

    tokens = [
        "LITERAL", "MACRO", "TEMPLATE_FUNC"
    ]

    @staticmethod
    def p_template_string(p):
        '''template_string : template_elems'''

    @staticmethod
    def p_template_elems(p):
        '''template_elems : template_elem template_elems
                          |'''

    @staticmethod
    def p_template_elem(p):
        '''template_elem : LITERAL
                         | MACRO
                         | TEMPLATE_FUNC
        '''

    def _construct_lexer(self):
        return TemplateLexer()
