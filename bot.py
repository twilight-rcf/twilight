import asyncio
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

TOKEN = "8868418702:AAF1gG7cAS-j7d43Qg_FHVna_7iGdp6B8zs"

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "автопринятие заявок в канал твайлайтов.\n"
        "потвердите что вы не робот для принятие заявки."
    )

# Срабатывает, когда кто-то подает заявку на вступление в канал
@dp.chat_join_request()
async def handle_join_request(chat_join: types.ChatJoinRequest):
    user = chat_join.from_user
    chat = chat_join.chat
    
    # Создаем кнопку подтверждения
    keyboard = InlineKeyboardBuilder()
    # Зашиваем в кнопку ID канала и ID пользователя
    keyboard.button(
        text="✅ Подтвердить, что я не робот", 
        callback_data=f"verify_{chat.id}_{user.id}"
    )
    
    try:
        # Telegram разрешает боту отправить сообщение в ЛС по chat_join.user_chat_id 
        # сразу после запроса на вступление (даже если пользователь не нажимал /start)
        await bot.send_message(
            chat_id=chat_join.user_chat_id,
            text=(
                f"Привет, {user.first_name}!\n\n"
                f"Чтобы подтвердить, что вы не робот, и получить доступ к каналу "
                f"«{chat.title}», нажмите кнопку ниже:"
            ),
            reply_markup=keyboard.as_markup()
        )
    except Exception as e:
        logging.error(f"Не удалось отправить сообщение в ЛС пользователю {user.id}: {e}")


# Обработка нажатия на кнопку в ЛС
@dp.callback_query(F.data.startswith("verify_"))
async def process_verification(callback: types.CallbackQuery):
    _, chat_id_str, user_id_str = callback.data.split("_")
    chat_id = int(chat_id_str)
    user_id = int(user_id_str)
    
    # Проверка, что нажимает именно тот пользователь
    if callback.from_user.id != user_id:
        await callback.answer("Эта кнопка не для вас!", show_alert=True)
        return

    try:
        # Автоматически одобряем заявку в канале
        await bot.approve_chat_join_request(chat_id=chat_id, user_id=user_id)
        
        # Меняем сообщение в чате с ботом
        await callback.message.edit_text(
            "✅ заявка в канал принята.\n"
            "можете переходить в канал.."
        )
        await callback.answer("Успешно!")
        
    except Exception as e:
        logging.error(f"Ошибка при подтверждении: {e}")
        await callback.answer("Произошла ошибка. Возможно, заявка уже была обработана.", show_alert=True)


async def main():
    logging.basicConfig(level=logging.INFO)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
  
