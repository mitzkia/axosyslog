
class SyslogFormat(object):
    @staticmethod
    def format_message(message, add_new_line=True):
        formatted_message = ""
        if message.priority_value:
            formatted_message += "<{}>".format(message.priority_value)
        if message.syslog_protocol_version:
            formatted_message += "{}".format(message.syslog_protocol_version)
        if message.iso_timestamp_value:
            formatted_message += " {}".format(message.iso_timestamp_value)
        if message.hostname_value:
            formatted_message += " {}".format(message.hostname_value)
        if message.program_value:
            formatted_message += " {}".format(message.program_value)
        if message.pid_value:
            formatted_message += " {}".format(message.pid_value)
        if message.message_id:
            formatted_message += " {}".format(message.message_id)
        if message.sdata:
            formatted_message += " {}".format(message.sdata)
        if message.message_value:
            formatted_message += " \uFEFF{}".format(message.message_value)
        if add_new_line:
            formatted_message += "\n"

        return "%d %s"% (len(formatted_message.encode("UTF8")), formatted_message)
