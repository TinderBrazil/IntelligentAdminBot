import asyncio
import settings

from random import randint, choice
from aiogram import Bot, Dispatcher
from aiogram import types
from aiogram.dispatcher.filters import IsReplyFilter, Text
from aiogram.utils import exceptions

from custom_filters import IsAdminFilter, ReadOnlyFilter, WelcomeFilter, ArgsCount
from models import Chat, ChatMember, UnregisteredMember

bot = Bot(settings.API_TOKEN)
dp = Dispatcher(bot)


async def ban_unregistered_member(chat_id, member_id):
    chat = Chat.get_chat(chat_id)
    await asyncio.sleep(chat.time_to_ban)

    try:
        UnregisteredMember.get(UnregisteredMember.user_id == member_id)
        member = await bot.get_chat_member(chat_id=chat_id, user_id=member_id)
        await bot.send_message(chat_id, f"I think {member.user.first_name} was bot...")
        await bot.kick_chat_member(chat_id, member_id)
    except UnregisteredMember.DoesNotExist:
        pass


@dp.message_handler(IsAdminFilter(can_restrict_members=True), IsReplyFilter(is_reply=True), commands=['ban'],
                    commands_prefix='!/')
async def ban_member(message: types.Message):
    try:
        await bot.kick_chat_member(message.chat.id, message.reply_to_message.from_user.id, until_date=5)
    except exceptions.UserIsAnAdministratorOfTheChat:
        await bot.send_message(message.chat.id, "User is an administrator of the chat.")
    else:
        await bot.send_message(message.chat.id, f"{message.from_user.first_name} <b>permentally</b> banned\
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
                                       f"{message.reply_to_message.from_user.full_name} has been banned.")
            except exceptions.UserIsAnAdministratorOfTheChat:
                await bot.send_message(message.chat.id, "OH, stop, I can't remove admin.")
                member.warnings = 0
        else:
            await bot.send_message(message.chat.id,
                                   f"{message.from_user.first_name} warned \
{message.reply_to_message.from_user.full_name} ({member.warnings}/{chat.warnings_to_ban}) "
                                   )
        member.save()


@dp.message_handler(IsReplyFilter(is_reply=True), commands=['unban'], commands_prefix='!/')
async def unban_member(message: types.Message):
    await bot.unban_chat_member(message.chat.id,
                                message.reply_to_message.from_user.id,
                                only_if_banned=True)

    await bot.send_message(message.chat.id, f"{message.from_user.first_name} unbanned \
    {message.reply_to_message.from_user.full_name}"
                           )


@dp.message_handler(commands=['stat'], commands_prefix='!/')
async def stat(message: types.Message):
    chat = Chat.get_chat(message.chat.id)
    message_text = f"Total messages: {chat.total_messages}\n\
Warnings to ban: {chat.warnings_to_ban}\nWelcome System: {'Enabled' if chat.welcome_system_enabled else 'disabled'}\
 \nBan time: {chat.time_to_ban} seconds\nTop of members by activity\n\n"
    counter = 1

    for i in chat.members.select().order_by(ChatMember.messages_count)[::-1][:10]:
        chat_member = await message.chat.get_member(i.user_id)
        message_text += f"{counter}. {chat_member.user.first_name} | {i.messages_count}\n"
        counter += 1

    await bot.send_message(message.chat.id, message_text)


@dp.message_handler(IsAdminFilter(), IsReplyFilter(is_reply=True), commands=['status'], commands_prefix='!/')
async def get_info(message: types.Message):
    member = ChatMember.get_member(message.chat.id, message.reply_to_message.from_user.id)
    chat = Chat.get_chat(message.chat.id)
    m = await bot.get_chat_member(message.chat.id, message.reply_to_message.from_user.id)
    message_text = f"User: {m.user.full_name}\nMessages from this user: {member.messages_count}\
\nReputation: {member.reputation}\n\
Warnings: {member.warnings}/{chat.warnings_to_ban}\n"
    await bot.send_message(message.chat.id, message_text)


@dp.message_handler(IsAdminFilter(can_delete_messages=True), IsReplyFilter(is_reply=True), commands=['mute'],
                    commands_prefix='/!')
async def mute_member(message: types.Message):
    try:
        await bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, can_send_messages=False)
    except exceptions.UserIsAnAdministratorOfTheChat:
        await bot.send_message(message.chat.id, "User is administrator...")
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


@dp.message_handler(ReadOnlyFilter())
async def delete_if_ro(message: types.Message):
    await bot.delete_message(message.chat.id, message.message_id)


@dp.message_handler(IsAdminFilter(), commands=['ws'], commands_prefix='!/')
async def welcome_system(message: types.Message):
    chat = Chat.get_chat(message.chat.id)
    chat.welcome_system_enabled = not chat.welcome_system_enabled
    chat.save()
    x = "enabled" if chat.welcome_system_enabled else "disabled"
    await bot.send_message(message.chat.id, f"{message.from_user.first_name} {x} welcome system.")


@dp.message_handler(IsAdminFilter(can_restrict_members=True), ArgsCount(1), 
                        commands=['setbantime'], commands_prefix='!/')
async def set_ban_time(message: types.Message):
    time = int(message.text.split()[1])
    chat = Chat.get_chat(message.chat.id)
    chat.time_to_ban = abs(time)
    chat.save()
    message_text = f"{message.from_user.first_name} changed bantime to {abs(time)}."
    await bot.send_message(message.chat.id, message_text)


@dp.message_handler(IsAdminFilter(), ArgsCount(1), commands=['setwarnstoban'], commands_prefix='!/')
async def set_warnings_to_ban(message: types.Message):
    chat = Chat.get_chat(message.chat.id)
    warns = abs(int(message.text.split()[1]))
    chat.warnings_to_ban = warns
    chat.save()
    message_text = f"{message.from_user.first_name} setted warnings for ban to {warns}."
    await bot.send_message(message.chat.id, message_text)


@dp.message_handler(WelcomeFilter(), content_types=types.ContentTypes.NEW_CHAT_MEMBERS)
async def captcha(message: types.Message):
    loop = asyncio.get_running_loop()
    a = randint(1, 9)
    b = randint(1, 9)
    member = UnregisteredMember.create(
        chat=Chat.get_chat(message.chat.id),
        user_id=message.from_user.id,
    )
    member.save()
    message_text = f"Hello {message.from_user.full_name}, for have chat with us, please solve this problem: {a}+{b} = ?"
    keyboard = types.InlineKeyboardMarkup()
    answers = [a + b, a + b - 1, a + b + 1]
    for i in range(3):
        x = choice(answers)
        keyboard.insert(types.InlineKeyboardButton(str(x), callback_data=f"captcha {message.from_user.id} \
{True if x == a + b else False}"))
        del answers[answers.index(x)]

    await bot.restrict_chat_member(
        message.chat.id,
        message.from_user.id,
        can_send_messages=False,
    )
    await message.reply(
        message_text,
        reply_markup=keyboard,
    )

    if Chat.get_chat(message.chat.id).time_to_ban:
        loop.create_task(ban_unregistered_member(message.chat.id, message.from_user.id))


@dp.callback_query_handler(Text(startswith='captcha'))
async def register_user(call: types.CallbackQuery):
    user_id = int(call.data.split()[1])
    ok = call.data.split()[2] == "True"

    if ok and user_id == call.from_user.id:
        t = UnregisteredMember.get(UnregisteredMember.user_id == user_id)
        t.delete_instance()

        await bot.restrict_chat_member(
            call.message.chat.id,
            call.from_user.id,
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True,
        )

        await call.answer(f"{call.from_user.first_name}, welcome to our chat!")
        await bot.delete_message(call.message.chat.id, call.message.message_id)


@dp.message_handler(content_types=types.ContentTypes.ANY)
async def handle(message: types.Message):
    chat = Chat.get_chat(message.chat.id)
    chat.total_messages += 1
    chat.save()

    # if message starts with +, we will increase reputation of user.
    if message.reply_to_message and \
            message.text.startswith('+') and message.from_user.id != message.reply_to_message.from_user.id:
        m = ChatMember.get_member(message.chat.id, message.reply_to_message.from_user.id)
        m.reputation += 1
        m.save()

    member = ChatMember.get_member(chat.chat_id, message.from_user.id)
    member.messages_count += 1
    member.save()
