class User:
    def __init__(self, ttl_msg, rep, identifier, enj_time):
        self.total_messages = ttl_msg
        self.reputation = rep
        self.id = identifier
        self.enj_time = enj_time

    def __repr__(self):
        return f"<User> {self.id}"


class Chat:
    def __init__(self, chat_id, ttl_msg, fw, rp_tr):
        self.chat_id = chat_id
        self.total_messages = ttl_msg
        self.fithy_words = fw
        self.reputation_triggers = rp_tr

    def __repr__(self):
        return f"<Chat> {self.chat_id}"
