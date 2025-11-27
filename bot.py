import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart

API_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 7153432300

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

def get_phone_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Оставить телефон", request_contact=True)]],
        resize_keyboard=True
    )

@dp.message(CommandStart())
async def start_cmd(message: Message):
    kb = get_phone_keyboard()
    await message.answer(
        "Привет! 👋\n"
        "Команда «3D Фигурки по фото» на связи.\n"
        "Напишите, какую фигурку хотите — мы скоро ответим!\n\n"
        "Чтобы менеджеру было проще связаться с вами — нажмите кнопку ниже и отправьте номер телефона 📱",
        reply_markup=kb
    )

@dp.message(F.text.startswith("/reply"))
async def reply_to_user(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("У вас нет прав использовать эту команду.")
        return

    parts = message.text.split(" ", 2)
    if len(parts) < 3:
        await message.answer("❗ Формат: /reply user_id текст")
        return

    user_id = int(parts[1])
    text = parts[2]

    await bot.send_message(user_id, text)
    await message.answer("✅ Ответ отправлен пользователю")

@dp.message(F.text)
async def handle_text(message: Message):
    if message.text.startswith("/reply"):
        return

    kb = get_phone_keyboard()
    await message.answer(
        "Спасибо! Ваше сообщение отправлено менеджеру 👌\n\n"
        "Чтобы мы быстрее связались с вами — оставьте свой номер телефона 📱",
        reply_markup=kb
    )

    username = f"@{message.from_user.username}" if message.from_user.username else "нет"
    text_for_admin = (
        "✉️ Новое сообщение от пользователя:\n"
        f"ID: {message.from_user.id}\n"
        f"Username: {username}\n\n"
        f"Текст:\n{message.text}"
    )
    await bot.send_message(ADMIN_ID, text_for_admin)

@dp.message(F.contact)
async def handle_contact(message: Message):
    contact = message.contact
    phone = contact.phone_number
    name = f"{contact.first_name or ''} {contact.last_name or ''}".strip()
    username = f"@{message.from_user.username}" if message.from_user.username else "нет"

    await message.answer(
        "Спасибо! Мы получили ваш номер телефона ✅\n"
        "Менеджер свяжется с вами в ближайшее время."
    )

    text_for_admin = (
        "📲 Новый контакт:\n"
        f"Имя: {name or 'не указано'}\n"
        f"Телефон: {phone}\n"
        f"Username: {username}\n"
        f"ID: {message.from_user.id}"
    )
    await bot.send_message(ADMIN_ID, text_for_admin)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
