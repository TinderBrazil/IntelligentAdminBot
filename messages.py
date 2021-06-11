messages = {
    'hello_msg': 
"""
Hello, I am IntelligentAdminBot, add me to your chat and give me admin rights.

Which commands I know?

/stat -> Get statistics and settings.
/ban (Must be reply to message) -> Ban member.
/mute (Must by reply to message) -> Mute member.
/warn -> Warn member.
/unban -> Unban member.
/unmute -> Unmute member.
/status (Must be reply to message) -> Get information about member.
/ws -> Enable/Disable Spammer-Protection System.
/setbantime -> Set specific ban time, set zero to disable it.
/setwarnstoban -> Set specific count of warnings to ban.

""",
    'stat_msg': 
"""Total messages: {ttl_msg}
Warnings to ban: {w_to_ban}
Welcome System: {ws}
Ban time: {tm_ban} seconds
Top of members by activity"
""",

'member_info': 
"""User: {full_name}
Messages from this user: {member_msg_count}
Reputation: {mem_rep}
Warnings: {warns}/{warns_to_ban}
""",

"enabled": "enabled",
"disabled": "disabled",
"ws_edit": "{name} {action} welcome system.",
"msg_ch_bantime": "{name} changed bantime to {new}.",
"invalid_arg": "Error, invalid argument provided.",

}

def get_message(message_type):
    """
    Just a pretty wrapper.
    Returns messages[message_type]
    """

    try:
        return messages[message_type]
    except KeyError:
        raise ValueError(f"Invalid message type: {message_type}")
