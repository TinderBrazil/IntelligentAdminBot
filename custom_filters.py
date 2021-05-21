from aiogram.dispatcher.filters import Filter
from aiogram import types
from models import Chat

class WelcomeSystemEnabled(Filter):
    async def check(self, message: types.Message):
        chat = Chat.get_chat(message.chat.id)
        return chat.welcome_system_enabled

class ReadOnlyFilter(Filter):
    async def check(self, message: types.Message):
        admins = [i.user.id for i in await message.chat.get_administrators()]
        return Chat.get_chat(message.chat.id).read_only and message.from_user.id not in admins

class IsAdminFilter(Filter):
    def __init__(self, can_restrict_members=False, can_promote_members=False, can_delete_messages=False):
        self.can_restirct_members = can_restrict_members
        self.can_delete_messages = can_delete_messages
        self.can_promote_members = can_promote_members
    
    async def check(self, message: types.Message):
        chat_admins = await message.bot.get_chat_administrators(message.chat.id)

        for admin in chat_admins:
            if admin.user.id == message.from_user.id:
                return (admin.can_promote_members != 0 or not self.can_promote_members) and\
                    (admin.can_delete_messages != 0 or not self.can_delete_messages) and \
                        (admin.can_restrict_members != 0 or not self.can_restirct_members)

        return False
