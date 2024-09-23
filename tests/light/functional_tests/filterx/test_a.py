import string

from hypothesis import given
from hypothesis import HealthCheck
from hypothesis import settings
from hypothesis import strategies as st
from hypothesis_jsonschema import from_schema



# "values.str" => string("string"),
# "values.bool" => boolean(true),
# "values.int" => int(111111111111111),
# "values.double" => double(32.5),
# "values.datetime" => datetime("1701350398.123000+01:00"),
# "values.list" => list("foo,bar,baz"),
# "values.null" => null(""),
# "values.bytes" => bytes("binary whatever"),
# "values.protobuf" => protobuf("this is not a valid protobuf!!"),
# "values.json" => json('{{"emb_key1": "emb_key1 value", "emb_key2": "emb_key2 value"}}'),
# "values.true_string" => string("boolean:true"),
# "values.false_string" => string("boolean:false"),

# +STRATEGY_MAPPING_BY_OPTION_TYPE = {
# +    "<float>": "floats(min_value=0.5, max_value=10000, allow_infinity=False, allow_nan=False)",
# +    "<nonnegative_integer>": "integers(min_value=0, max_value=2147483648)",
# +    "<number>": "integers(max_value=9223372036854775807)",
# +    "<positive_integer>": "integers(min_value=1, max_value=2147483648)",
# +
# +    "<string>": 'text(alphabet=string.printable, min_size=1).filter(lambda item: "\'" not in item and "\\"" not in item and "`" not in item)',
# +    "<path>": "text(alphabet=string.printable)",
# +    "<string_list>": "lists(text(alphabet=string.ascii_letters + string.digits, min_size=15, max_size=15).map(repr), min_size=1).map(' '.join)",
# +    "<string_or_number>": "one_of(integers(), text(alphabet=string.printable, min_size=1), floats())",
# +    "<template_content>": 'template_functions()',
# +    "<yesno>": 'one_of(integers(min_value=-9223372036854775807 ,max_value=9223372036854775807), sampled_from(["yes", "no", "on", "off", 0, 1]))',
# +
# +    "<empty>": "just(None)",
# +    "<arrow>": "just('=>')",
# +    "<:>": "just(':')",                                                                                                                                                                                                                                    +    "<unknown>": "text(alphabet=string.ascii_letters)",
# +    "<identifier>": "text(alphabet=string.ascii_letters)",

def gen_str():
    return st.text(alphabet=string.printable, min_size=1).filter(lambda item: "\'" not in item and "\"" not in item and "`" not in item)

def gen_boolean():
    return st.booleans()

def gen_int():
    return st.integers(max_value=9223372036854775807, min_value=-9223372036854775808)

def gen_double():
    return st.floats(min_value=-1.7976931348623157E+308, max_value=1.7976931348623157E+308, allow_infinity=False, allow_nan=False)

def gen_datetime():
    return st.datetimes()

@given(s=gen_str())
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=5, database=None, deadline=None)
def test_a(config, syslog_ng, syslog_ng_ctl, s):
    config.reset()
    config.update_global_options(stats="level(5)")
    generator_source = config.create_example_msg_generator_source(num=1, values='"values.str" => string("%s")' % s)
    file_destination = config.create_file_destination(file_name="output.log", template="'$MSG\n'")

    config.create_logpath(statements=[generator_source, file_destination])
    syslog_ng.start(config)

    # log = file_destination.read_log()
    # assert log == generator_source.DEFAULT_MESSAGE + "\n"
    # syslog_ng.reload(config)

    # print(file_destination.read_log())
    # syslog_ng_ctl.query()
    assert file_destination.get_query()["written"] == 1
    syslog_ng.stop()


# { "PONumber"             : 1600,
#   "Reference"            : "ABULL-20140421",
#   "Requestor"            : "Alexis Bull",
#   "User"                 : "ABULL",
#   "CostCenter"           : "A50",
#   "ShippingInstructions" : { "name"   : "Alexis Bull",
#                              "Address": { "street"  : "200 Sporting Green",
#                                           "city"    : "South San Francisco",
#                                           "state"   : "CA",
#                                           "zipCode" : 99236,
#                                           "country" : "United States of America" },
#                              "Phone" : [ { "type"   : "Office", 
#                                            "number" : "909-555-7307" },
#                                          { "type"   : "Mobile",
#                                            "number" : "415-555-1234" } ] },
#   "Special Instructions" : null,
#   "AllowPartialShipment" : false,
#   "LineItems"            : [ { "ItemNumber" : 1,
#                                "Part"       : { "Description" : "One Magic Christmas",
#                                                 "UnitPrice"   : 19.95,
#                                                 "UPCCode"     : 13131092899 },
#                                "Quantity"   : 9.0 },
#                              { "ItemNumber" : 2,
#                                "Part"       : { "Description" : "Lethal Weapon",
#                                                 "UnitPrice"   : 19.95,
#                                                 "UPCCode"     : 85391628927 },
#                                "Quantity"   : 5.0 } ] }

@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=50, database=None)
# @given(from_schema({"$schema": "http://json-schema.org/draft-06/schema"}))
@given(from_schema({"$schema": '{ "PONumber" : 1600 }'}))
# @given(value=from_schema({"type": "dict", "pattern": "^[a-zA-Z0-9]+$"}))
def test_filterx_b(config, syslog_ng, value):
    config.reset()
    syslog_ng.stop()

    config.update_global_options(stats="level(5)")
    generator_source = config.create_example_msg_generator_source(num=1, values="'values.json' => json('%s')" % value)
    filterx_content = """
        $envelope = "$(format-json --subkeys values.)";
        $MSG = $envelope.json;
"""
    filterx_item = config.create_filterx(filterx_content)
    file_destination = config.create_file_destination(file_name="output.log", template="'$MSG\n'")

    config.create_logpath(statements=[generator_source, filterx_item, file_destination])
    syslog_ng.start(config)


    syslog_ng.stop()
    # log = file_destination.read_log()
    # assert log == generator_source.DEFAULT_MESSAGE + "\n"
    # syslog_ng.reload(config)

    # print(file_destination.read_log())
    # syslog_ng_ctl.query()
    # assert file_destination.get_query()["written"] == 1
    # syslog_ng.stop()
