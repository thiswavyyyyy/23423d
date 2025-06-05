from aiogram import types
from aiogram.dispatcher import FSMContext

from config import SUPPORT_CHAT_ID
from handlers.support.functions import SupportRequest
from loader import dp
from states import SupportState



@dp.message_handler(commands=["start", "support", "help"])
async def main_command(message: types.Message):
    await message.reply(
        text="💎 Добро пожаловать в поддержку YASplitShop.\n\n"
            "❗️ Напишите свой вопрос, пожалуйста пишите Ваш вопрос одним сообщением.",
    )
    await SupportState.send_request.set()


@dp.message_handler(
    state=SupportState.send_request, content_types=types.ContentType.ANY
)
async def send_request(message: types.Message, state: FSMContext):
    support_request = SupportRequest(
        user_id=message.from_user.id,
        username=message.from_user.username,
        message_id=message.message_id,
    )
    await support_request.send_support_request()
    await message.reply(text="💌 Ваш запрос отправлен.\n\n 💤 Свободный Менеджер по возможности ответит Вам.")
    await state.finish()


@dp.message_handler(state=SupportState.in_support, content_types=types.ContentType.ANY)
async def support_reply(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    message_thread_id = state_data.get("message_thread_id")
    await dp.bot.forward_message(
        from_chat_id=message.chat.id,
        message_thread_id=message_thread_id,
        chat_id=SUPPORT_CHAT_ID,
        message_id=message.message_id,
    )
