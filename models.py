import peewee
import logging
import settings

db = peewee.SqliteDatabase(settings.DB_FILENAME)


class Base(peewee.Model):
    class Meta:
        database = db


class Chat(Base):
    chat_id = peewee.IntegerField(unique=True)
    total_messages = peewee.IntegerField(default=0)

    # base chat settings
    warnings_to_ban = peewee.IntegerField(default=3)
    welcome_system_enabled = peewee.BooleanField(default=True)
    only_admins_can_see_rating = peewee.BooleanField(default=False)
    read_only = peewee.BooleanField(default=False)
    time_to_ban = peewee.IntegerField(default=20)

    @staticmethod
    def get_chat(chat_id):
        try:
            return Chat.select().where(Chat.chat_id == chat_id).get()
        except Chat.DoesNotExist:
            logging.info(f"Chat created, {chat_id}")
            chat = Chat.create(chat_id=chat_id)
            chat.save()
            return chat


class ChatMember(Base):
    chat = peewee.ForeignKeyField(Chat, backref='members')
    user_id = peewee.IntegerField()
    messages_count = peewee.IntegerField(default=0)
    reputation = peewee.IntegerField(default=0)
    warnings = peewee.IntegerField(default=0)

    @staticmethod
    def get_member(chat_id, user_id):
        try:
            return Chat.get_chat(chat_id).members.select().where(ChatMember.user_id == user_id).get()
        except ChatMember.DoesNotExist:
            logging.info(f"Created member: {user_id} in {chat_id}")
            return ChatMember.create(chat=Chat.get_chat(chat_id), user_id=user_id, messages_count=0)


class UnregisteredMember(Base):
    chat = peewee.ForeignKeyField(Chat, backref='unregistered_members')
    user_id = peewee.IntegerField(unique=True)
