import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart

# 🔹 ДАННЫЕ
API_TOKEN = "8595739286:AAHwQoWMqpj3lvc-FPzVT4OAWTxBI8CsMXY"
ADMIN_ID = 7153432300  # твой Telegram ID

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()


# 🔹 Кнопка "Оставить телефон"
def get_phone_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Оставить телефон", request_contact=True)]
        ],
        resize_keyboard=True
    )


# 🔹 /start
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


# 🔹 Ответ от менеджера: /reply user_id текст
@dp.message(F.text.startswith("/reply"))
async def reply_to_user(message: Message):
    # Разрешаем пользоваться командой только админу
    if message.from_user.id != ADMIN_ID:
        await message.answer("У вас нет прав использовать эту команду.")
        return

    parts = message.text.split(" ", 2)

    if len(parts) < 3:
        await message.answer("❗ Формат: /reply user_id текст_ответа")
        return

    try:
        user_id = int(parts[1])
    except ValueError:
        await message.answer("❗ user_id должен быть числом.")
        return

    text = parts[2]

    try:
        await bot.send_message(user_id, text)
        await message.answer("✅ Ответ отправлен пользователю")
    except Exception as e:
        await message.answer(f"Ошибка при отправке: {e}")


# 🔹 Любой текст от клиента
@dp.message(F.text)
async def handle_text(message: Message):
    # Если это команда /reply от тебя — её уже обработал предыдущий хендлер
    if message.text.startswith("/reply"):
        return

    kb = get_phone_keyboard()

    # Ответ клиенту
    await message.answer(
        "Спасибо! Ваше сообщение отправлено менеджеру 👌\n\n"
        "Чтобы мы быстрее связались с вами — оставьте, пожалуйста, свой номер телефона 📱",
        reply_markup=kb
    )

    # Сообщение админу
    try:
        username = f"@{message.from_user.username}" if message.from_user.username else "нет"
        text_for_admin = (
            "✉️ Новое сообщение от пользователя:\n"
            f"ID: {message.from_user.id}\n"
            f"Username: {username}\n\n"
            f"Текст:\n{message.text}"
        )
        await bot.send_message(ADMIN_ID, text_for_admin)
    except Exception as e:
        print("Ошибка при отправке сообщения админу:", e)


# 🔹 Клиент отправил контакт (номер телефона кнопкой)
@dp.message(F.contact)
async def handle_contact(message: Message):
    contact = message.contact
    phone = contact.phone_number
    name = f"{contact.first_name or ''} {contact.last_name or ''}".strip()
    username = f"@{message.from_user.username}" if message.from_user.username else "нет"

    # Ответ клиенту
    await message.answer(
        "Спасибо! Мы получили ваш номер телефона ✅\n"
        "Менеджер свяжется с вами в ближайшее время."
    )

    # Отправка админу
    try:
        text_for_admin = (
            "📲 Новый контакт от пользователя:\n"
            f"Имя: {name or 'не указано'}\n"
            f"Телефон: {phone}\n"
            f"Username: {username}\n"
            f"ID: {message.from_user.id}"
        )
        await bot.send_message(ADMIN_ID, text_for_admin)
    except Exception as e:
        print("Ошибка при отправке контакта админу:", e)


async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
