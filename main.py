"""
    IntelligentBot version 0.1
    Written by WinDuz
    2021
"""

import asyncio
import settings
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import Message, ChatPermissions
from aiogram.dispatcher.filters import IsReplyFilter
from dbcontroller import DBController
from customfilters import AdminCommand

bot = Bot(settings.API_TOKEN)
dp = Dispatcher(bot)
db = DBController(settings.DB_FILENAME)


@dp.message_handler(AdminCommand(), commands=['ban'], commands_prefix='!/')
async def ban_by_message(message: Message):
    user_for_kick = message.reply_to_message.from_user
    if user_for_kick.id != message.from_user.id:
        await bot.kick_chat_member(message.chat.id, user_for_kick.id)
        await bot.send_message(message.chat.id, f'Пользователь <b>"@{user_for_kick.username}"</b> заблокирован!',
                               parse_mode='html')
    else:
        await message.reply("Я все понимаю, но так нельзя.")


@dp.message_handler(AdminCommand(), commands=['unban'], commands_prefix='!/')
async def unban_user(message: Message):
    user_for_unban = message.reply_to_message.from_user
    await bot.unban_chat_member(message.chat.id, user_for_unban.id)
    print(message.chat.id)
    await bot.send_message(message.chat.id, f'Пользователь "@{user_for_unban.username}" разблокирован.')


@dp.message_handler(AdminCommand(), commands=['mute'], commands_prefix='!/')
async def mute_user(message: Message):
    to_user = message.reply_to_message.from_user
    await bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id,
                                   ChatPermissions(can_send_messages=False))
    await bot.send_message(message.chat.id, f"Пользователь @{to_user.username} лишен прав писать в чат.")


@dp.message_handler(AdminCommand(), commands=['unmute'], commands_prefix='!/')
async def unmute_user(message: Message):
    to_user = message.reply_to_message.from_user
    await bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id,
                                   ChatPermissions(can_send_messages=True))
    await bot.send_message(message.chat.id, f"Пользователь @{to_user.username} снова может писать в чате!")


@dp.message_handler(IsReplyFilter(is_reply=True), commands=['promote'], commands_prefix='!/')
async def promote_user(message: Message):
    user = await bot.get_chat_member(message.chat.id, message.from_user.id)
    to = message.reply_to_message
    if user.status != 'creator':
        await message.reply("Только создатель чата может заниматься промоутингом.")
    else:
        await bot.promote_chat_member(message.chat.id, to.from_user.id, 
            can_delete_messages=True, 
            can_promote_members=True, 
            can_restrict_members=True,
            can_change_info=True,
            can_pin_messages=True,
            )
        await bot.send_message(message.chat.id, f"Теперь @{to.from_user.username} администратор чата!")

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(dp.start_polling())
    loop.run_forever()
