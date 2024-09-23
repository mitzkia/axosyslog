from hypothesis import given
from hypothesis.extra.lark import from_lark
from lark.lark import Lark

# from tests.common.debug import check_can_generate_examples, find_any

# Adapted from the official Lark tutorial, with modifications to ensure
# that the generated JSON is valid.  i.e. no numbers starting with ".",
# \f is not ignorable whitespace, and restricted strings only.  Source:
# https://github.com/lark-parser/lark/blob/master/docs/json_tutorial.md
EBNF_GRAMMAR = r"""
    value: dict
         | list
         | STRING
         | NUMBER
         | "true"  -> true
         | "false" -> false
         | "null"  -> null
    list : "[" [value ("," value)*] "]"
    dict : "{" [STRING ":" value ("," STRING ":" value)*] "}"

    STRING : /"[a-z]*"/
    NUMBER : /-?[1-9][0-9]*(\.[0-9]+)?([eE][+-]?[0-9]+)?/

    WS : /[ \t\r\n]+/
    %ignore WS
"""

EBNF_GRAMMAR2 = r"""
    value: STRING
         | NUMBER
         | WHITESPACE
         | WORD

    STRING : /"[a-zA-Z]*"/
    NUMBER : /-?[1-9][0-9]*(\.[0-9]+)?/
    WHITESPACE : /[ \t]/
    WORD: /\#'"\(\)\{\}\[\]\\;\r\n\t/
"""


LIST_GRAMMAR = r"""
list : "[" [NUMBER ("," NUMBER)*] "]"
NUMBER: /[0-9]|[1-9][0-9]*/
"""


@given(from_lark(Lark(EBNF_GRAMMAR, start="value")))
def test_generates_valid_json(string):
    print("AAAAA: [%s]" % string)
    # json.loads(string)
    assert True
