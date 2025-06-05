from aiogram import types
from aiogram.dispatcher.filters import Text

from config import SUPPORT_CHAT_ID
from db_logic.base import SupportTickets
from loader import dp
from states import SupportState


# выводить chat_id при добавлении в новую группу
@dp.message_handler(content_types=types.ContentType.NEW_CHAT_MEMBERS)
async def new_chat_member(message: types.Message):
    await message.reply(f"ID чата для .env: {message.chat.id}\n"
                        f"Не забудьте сделать бота администратором!")


@dp.message_handler(chat_id=SUPPORT_CHAT_ID, content_types=types.ContentType.ANY)
async def support_admin_reply(message: types.Message):
    if message.content_type in [
        types.ContentType.FORUM_TOPIC_CREATED,
        types.ContentType.FORUM_TOPIC_EDITED,
        types.ContentType.FORUM_TOPIC_CLOSED,
    ]:
        return
    message_thread_id = message.message_thread_id
    ticket = SupportTickets().get_ticket_by_message_thread_id(message_thread_id)
    if ticket:
        user_state = dp.current_state(chat=ticket.tg_id, user=ticket.tg_id)
        await user_state.set_state(SupportState.in_support)
        await user_state.update_data(message_thread_id=message_thread_id)
        try:
            # Если сообщение содержит фото, отправляем фото клиенту
            if message.content_type == types.ContentType.PHOTO:
                photo_id = message.photo[-1].file_id
                caption = f"🌄 Фотография от Менеджера: {message.caption}" if message.caption else "🌄 Фотография от Менеджера:"
                await dp.bot.send_photo(
                    chat_id=ticket.tg_id,
                    photo=photo_id,
                    caption=caption
                )
            # Если сообщение содержит видео, отправляем видео клиенту
            elif message.content_type == types.ContentType.VIDEO:
                video_id = message.video.file_id
                caption = f"🎥 Видео от Менеджера: {message.caption}" if message.caption else "🎥 Видео от Менеджера:"
                await dp.bot.send_video(
                    chat_id=ticket.tg_id,
                    video=video_id,
                    caption=caption
                )
            # Если сообщение содержит другие типы контента, отправляем текстовое сообщение
            else:
                await dp.bot.send_message(
                    chat_id=ticket.tg_id,
                    text=f"👁️ У Вас новое сообщение от Менеджера: {message.text}"
                )
        except Exception as _ex:
            await message.answer(
                text=f"Не удалось доставить сообщение пользователю: {_ex}"
            )
    else:
        await message.reply(text="Тикет не найден")


@dp.callback_query_handler(Text(equals="close_ticket"), state="*")
async def close_ticket(call: types.CallbackQuery):
    ticket = SupportTickets().get_ticket_by_message_thread_id(
        call.message.message_thread_id
    )
    if ticket:
        user_state = dp.current_state(chat=ticket.tg_id, user=ticket.tg_id)
        await user_state.finish()
        await dp.bot.send_message(
            chat_id=ticket.tg_id,
            text="🔒️ Ваш тикет был закрыт.\n\n ❓️ Если у Вас остались вопросы напишите в чат /start"
        )
        await dp.bot.delete_forum_topic(
            chat_id=SUPPORT_CHAT_ID,
            message_thread_id=call.message.message_thread_id
        )
        SupportTickets().delete_ticket(call.message.message_thread_id)
    else:
        await call.answer(text="Тикет не найден")