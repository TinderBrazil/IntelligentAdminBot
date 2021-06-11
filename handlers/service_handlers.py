from bot import dp, bot
from aiogram import types
from messages import get_message
from models import *
from custom_filters import *
from aiogram.dispatcher.filters import *


@dp.message_handler(commands=['start', 'help'])
async def help(message: types.Message):
    await bot.send_message(message.chat.id, get_message('help_msg'))


@dp.message_handler(commands=['stat'], commands_prefix='!/')
async def stat(message: types.Message):
    chat = Chat.get_chat(message.chat.id)

    message_text = get_message("stat_msg").format(
        chat.total_messages,
        chat.warnings_to_ban,
        chat.welcome_system_enabled,
        chat.time_to_ban,
    )

    counter = 1

    for i in chat.members.select().order_by(ChatMember.messages_count)[::-1][:10]:
        chat_member = await message.chat.get_member(i.user_id)
        message_text += f"{counter}. {chat_member.user.first_name} | {i.messages_count}\n"
        counter += 1

    await bot.send_message(message.chat.id, message_text)


@dp.message_handler(IsAdminFilter(), IsReplyFilter(is_reply=True), commands=['status'], commands_prefix='!/')
async def get_info(message: types.Message):
    member = ChatMember.get_member(
        message.chat.id, message.reply_to_message.from_user.id)
    chat = Chat.get_chat(message.chat.id)
    m = await bot.get_chat_member(message.chat.id, message.reply_to_message.from_user.id)

    message_text = get_message('member_info').format(
        m.user.full_name,
        member.messages_count,
        member.reputation,
        member.warnings,
        chat.warnings_to_ban,
    )

    await bot.send_message(message.chat.id, message_text)
