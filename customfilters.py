from aiogram.dispatcher.filters import Filter
from aiogram.types import Message


class AdminCommand(Filter):
    async def check(self, message: Message):
        bot = message.bot
        admins = [i.user.id for i in await bot.get_chat_administrators(message.chat.id)]
        reply_to = message.reply_to_message

        if message.from_user.id not in admins:
            await message.reply("Вам необходимо дорости до администратора 😁")
            return False

        if not reply_to:
            await message.reply("Сообщение должно быть ответом на <b>другое</b> сообщение.")
            return False

        if reply_to.from_user.id == message.from_user.id:
            await message.reply("Я прекрасно тебя понимаю...\n<b>Но и ты меня пойми!</b>", parse_mode='html')
            return

        if reply_to.from_user.id in admins:
            await message.reply(
                "Данная команда не может быть применена к данному типу юзеров, на этом наши полномочия - всё!")
            return False

        return True