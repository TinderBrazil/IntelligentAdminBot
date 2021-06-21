import asyncio

from bot import dp, bot
from models import *
from aiogram.utils import exceptions
from custom_filters import *
from aiogram.dispatcher.filters import IsReplyFilter

async def ban_unregistered_member(chat_id, member_id):
    chat = Chat.get_chat(chat_id)
    await asyncio.sleep(chat.time_to_ban)

    try:
        UnregisteredMember.get(UnregisteredMember.user_id == member_id)
        member = await bot.get_chat_member(chat_id=chat_id, user_id=member_id)
        await bot.send_message(chat_id, f"eu acho que {member.user.first_name} foi bot ... ")
        await bot.kick_chat_member(chat_id, member_id)
    except UnregisteredMember.DoesNotExist:
        pass


@dp.message_handler(IsAdminFilter(can_restrict_members=True), IsReplyFilter(is_reply=True), commands=['ban'],
                    commands_prefix='!/')
async def ban_member(message: types.Message):
    try:
        await bot.kick_chat_member(message.chat.id, message.reply_to_message.from_user.id, until_date=5)
    except exceptions.UserIsAnAdministratorOfTheChat:
        await bot.send_message(message.chat.id, "O usuário é um administrador do chat.")
    else:
        await bot.send_message(message.chat.id, f"{message.from_user.first_name} <b>permentalmente</b> banido\
    {message.reply_to_message.from_user.full_name}", parse_mode='html')


@dp.message_handler(IsReplyFilter(is_reply=True), IsAdminFilter(can_restrict_members=True), commands=['warn'],
                    commands_prefix='!/')
async def warn_member(message: types.Message):
    if message.from_user.id != message.reply_to_message.from_user.id:
        member = ChatMember.get_member(message.chat.id, message.reply_to_message.from_user.id)
        chat = Chat.get_chat(message.chat.id)
        member.warnings += 1
        if chat.warnings_to_ban == member.warnings:
            member.warnings = 0
            try:
                await bot.kick_chat_member(message.chat.id, message.reply_to_message.from_user.id)
                await bot.send_message(message.chat.id,
                                       f"{message.reply_to_message.from_user.full_name} foi banido.")
            except exceptions.UserIsAnAdministratorOfTheChat:
                await bot.send_message(message.chat.id, "OH, pare, não consigo remover o admin.")
                member.warnings = 0
        else:
            await bot.send_message(message.chat.id,
                                   f"{message.from_user.first_name} avisou \
{message.reply_to_message.from_user.full_name} ({member.warnings}/{chat.warnings_to_ban}) "
                                   )
        member.save()





@dp.message_handler(IsReplyFilter(is_reply=True), commands=['unban'], commands_prefix='!/')
async def unban_member(message: types.Message):
    await bot.unban_chat_member(message.chat.id,
                                message.reply_to_message.from_user.id,
                                only_if_banned=True)

    await bot.send_message(message.chat.id, f"{message.from_user.first_name} não banido \
    {message.reply_to_message.from_user.full_name}"
                           )



@dp.message_handler(IsAdminFilter(can_delete_messages=True), IsReplyFilter(is_reply=True), commands=['mute'],
                    commands_prefix='/!')
async def mute_member(message: types.Message):
    try:
        await bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, can_send_messages=False)
    except exceptions.UserIsAnAdministratorOfTheChat:
        await bot.send_message(message.chat.id, "O usuário é administrador...")
    else:
        await bot.send_message(message.chat.id,
                               f"{message.from_user.first_name} muted {message.reply_to_message.from_user.full_name}\
forever.")


@dp.message_handler(IsAdminFilter(can_delete_messages=True), IsReplyFilter(is_reply=True), commands=['unmute'],
                    commands_prefix='/!')
async def unmute_member(message: types.Message):
    await bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id,
                                   can_send_messages=True,
                                   can_add_web_page_previews=True,
                                   can_send_media_messages=True,
                                   can_send_other_messages=True
                                   )
    await bot.send_message(message.chat.id,
                           f"{message.from_user.first_name} umuted {message.reply_to_message.from_user.full_name}")


@dp.message_handler(IsAdminFilter(can_delete_messages=True), commands=['ro', 'readonly'], commands_prefix='/!')
async def readonly(message: types.Message):
    chat = Chat.get_chat(message.chat.id)
    chat.read_only = not chat.read_only
    tp = "enabled" if chat.read_only else "disabled"
    chat.save()
    await bot.send_message(message.chat.id, f"{message.from_user.first_name} {tp} readonly-mode.")


@dp.message_handler(IsAdminFilter(can_restrict_members=True), IsReplyFilter(is_reply=True), commands=['kick'],
                    commands_prefix='!/')
async def kick_member(message: types.Message):
    try:
        await bot.kick_chat_member(message.chat.id, message.reply_to_message.from_user.id)
        await bot.unban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
    except exceptions.UserIsAnAdministratorOfTheChat:
        await bot.send_message(message.chat.id, "User is admin.")
    else:
        await bot.send_message(message.chat.id,
                               f"{message.from_user.first_name} kicked {message.reply_to_message.from_user.full_name}")
