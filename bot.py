import settings

from aiogram import Bot, Dispatcher
from aiogram.utils import exceptions
from aiogram.dispatcher.filters import IsReplyFilter
from aiogram import types
from models import Chat, ChatMember
from custom_filters import IsAdminFilter, ReadOnlyFilter


bot = Bot(settings.API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(IsAdminFilter(can_restrict_members=True), IsReplyFilter(is_reply=True), commands=['ban'], commands_prefix='!/')
async def ban_member(message: types.Message):
    try:
        await bot.kick_chat_member(message.chat.id, message.reply_to_message.from_user.id, until_date=5)
    except exceptions.UserIsAnAdministratorOfTheChat:
        await bot.send_message(message.chat.id, "User is an administrator of the chat.")
    else:
        await bot.send_message(message.chat.id, f"{message.from_user.first_name} <b>permentally</b> banned\
    {message.reply_to_message.from_user.full_name}", parse_mode='html')


@dp.message_handler(IsReplyFilter(is_reply=True), commands=['unban'], commands_prefix='!/')
async def unban_member(message: types.Message):
    await bot.unban_chat_member(message.chat.id, 
        message.reply_to_message.from_user.id, 
        only_if_banned=True)
    
    await bot.send_message(message.chat.id, f"{message.from_user.first_name} unbanned \
    {message.reply_to_message.from_user.full_name}" \
    )


@dp.message_handler(commands=['stat'])
async def stat(message: types.Message):
    chat = Chat.get_chat(message.chat.id)

    message_text = f"Total messages: {chat.total_messages}\n\nTop of members by activity\n"
    counter = 1

    for i in chat.members.select().order_by(ChatMember.messages_count)[::-1][:10]:
        chat_member = await message.chat.get_member(i.user_id)
        message_text += f"{counter}. {chat_member.user.first_name} | {i.messages_count}\n"
        counter += 1
    
    await bot.send_message(message.chat.id, message_text)


@dp.message_handler(IsAdminFilter(), IsReplyFilter(is_reply=True), commands=['status'])
async def get_info(message: types.Message):
    member = ChatMember.get_member(message.chat.id, message.reply_to_message.from_user.id)
    m = await bot.get_chat_member(message.chat.id, message.reply_to_message.from_user.id)
    message_text = f"User: {m.user.full_name}\nMessages from this user: {member.messages_count}\
\nReputation: {member.reputation}"
    await bot.send_message(message.chat.id, message_text)


@dp.message_handler(IsAdminFilter(can_delete_messages=True), IsReplyFilter(is_reply=True), commands=['mute'], commands_prefix='/!')
async def mute_member(message: types.Message):
    try:
        await bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, can_send_messages=False)
    except exceptions.UserIsAnAdministratorOfTheChat:
        await bot.send_message(message.chat.id, "User is administrator...")
    else:
        await bot.send_message(message.chat.id, f"{message.from_user.first_name} \
    muted {message.reply_to_message.from_user.full_name} forever.")


@dp.message_handler(IsAdminFilter(can_delete_messages=True), IsReplyFilter(is_reply=True), commands=['unmute'], commands_prefix='/!')
async def unmute_member(message: types.Message):
    await bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, can_send_messages=True)
    await bot.send_message(message.chat.id, f"{message.from_user.first_name} umuted {message.reply_to_message.from_user.full_name}")


@dp.message_handler(IsAdminFilter(can_delete_messages=True), commands=['ro', 'readonly'], commands_prefix='/!')
async def readonly(message: types.Message):
    chat = Chat.get_chat(message.chat.id)
    chat.read_only = not chat.read_only
    tp = "enabled" if chat.read_only else "disabled"
    chat.save()
    await bot.send_message(message.chat.id, f"{message.from_user.first_name} {tp} readonly-mode.")


@dp.message_handler(IsAdminFilter(can_restrict_members=True), IsReplyFilter(is_reply=True), commands=['kick'], commands_prefix='!/')
async def kick_member(message: types.Message):
    try:
        await bot.kick_chat_member(message.chat.id, message.reply_to_message.from_user.id)
        await bot.unban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
    except exceptions.UserIsAnAdministratorOfTheChat:
        await bot.send_message(message.chat.id, "User is admin.")
    else:
        await bot.send_message(message.chat.id, f"{message.from_user.first_name} kicked {message.reply_to_message.from_user.full_name}")


@dp.message_handler(ReadOnlyFilter())
async def delete_if_ro(message: types.Message):
    await bot.delete_message(message.chat.id, message.message_id)


@dp.message_handler()
async def handle(message: types.Message):
    chat = Chat.get_chat(message.chat.id)
    chat.total_messages += 1
    chat.save()

    if message.reply_to_message and \
        message.text.startswith('+') and message.from_user.id != message.reply_to_message.from_user.id:
        m = ChatMember.get_member(message.chat.id, message.reply_to_message.from_user.id)
        m.reputation += 1
        m.save()        

    member = ChatMember.get_member(chat.chat_id, message.from_user.id)
    member.messages_count += 1
    member.save()