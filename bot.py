import asyncio
import settings

from aiogram import Bot, Dispatcher
from aiogram import types
from aiogram.dispatcher.filters import IsReplyFilter, Text
from aiogram.utils import exceptions

from custom_filters import IsAdminFilter, ReadOnlyFilter, WelcomeFilter, ArgsCount
from random import randint, choice
from models import Chat, ChatMember, 
from messages import get_message

bot = Bot(settings.API_TOKEN)
dp = Dispatcher(bot)





@dp.message_handler(ReadOnlyFilter())
async def delete_if_ro(message: types.Message):
    await bot.delete_message(message.chat.id, message.message_id)


@dp.message_handler(WelcomeFilter(), content_types=types.ContentTypes.NEW_CHAT_MEMBERS)
async def captcha(message: types.Message):
    loop = asyncio.get_running_loop()
    await message.delete()
    a, b = randint(1, 9), b = randint(1, 9)
    member = UnregisteredMember.create(
        chat=Chat.get_chat(message.chat.id),
        user_id=message.from_user.id,
    )
    member.save()
    message_text = f"Hello {message.from_user.full_name}, for have chat with us, please solve this problem: {a}+{b} = ?"
    keyboard = types.InlineKeyboardMarkup()
    answers = [a + b, a + b - 1, a + b + 1]
    
    for _ in range(3):
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
        await call.message.delete()


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
