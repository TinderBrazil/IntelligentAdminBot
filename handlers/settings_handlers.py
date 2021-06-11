from peewee import Value
from messages import get_message
from bot import bot, dp
from models import *
from custom_filters import *


@dp.message_handler(IsAdminFilter(can_restrict_members=True), commands=['ws'], commands_prefix='!/')
async def welcome_system(message: types.Message):
    chat = Chat.get_chat(message.chat.id)
    chat.welcome_system_enabled = not chat.welcome_system_enabled
    action = get_message('enabled') if chat.welcome_system_enabled else get_message('disalbed')
    msg_text = get_message("ws_edit").format(message.from_user.first_name, action)
    await bot.send_message(message.chat.id, msg_text)
    chat.save()


@dp.message_handler(IsAdminFilter(can_restrict_members=True), ArgsCount(1), 
                        commands=['setbantime'], commands_prefix='!/')
async def set_ban_time(message: types.Message):
    try:
        time = int(message.text.split()[1])
    except ValueError:
        await message.reply(get_message('invalid_arg'))
        return

    chat = Chat.get_chat(message.chat.id)
    chat.time_to_ban = abs(time) # speccially for t.me/w3bdev
    message_text = get_message('msg_ch_bantime').format(message.from_user.first_name, chat.time_to_ban)
    await bot.send_message(message.chat.id, message_text)
    chat.save()


@dp.message_handler(IsAdminFilter(), ArgsCount(1), commands=['setwarnstoban'], commands_prefix='!/')
async def set_warnings_to_ban(message: types.Message):
    chat = Chat.get_chat(message.chat.id)
    warns = abs(int(message.text.split()[1]))
    chat.warnings_to_ban = warns
    message_text = f"{message.from_user.first_name} setted warnings for ban to {warns}."
    await bot.send_message(message.chat.id, message_text)
    chat.save()
