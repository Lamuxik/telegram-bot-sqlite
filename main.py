import database
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
MASTER_ID = int(os.getenv("MASTER_ID"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

database.init_db()

@dp.message(Command("new"))
async def show_new_applications(message: Message):
    if message.from_user.id != MASTER_ID:
        await message.answer("У вас нет доступа.")
        return

    applications = database.get_new_applications()

    if not applications:
        await message.answer("Новых заявок нет.")
        return

    for application in applications:
        application_id, client_name, problem = application

        keyboard = InlineKeyboardBuilder()

        keyboard.button(
            text="✅ Взять заказ",
            callback_data=f"accept:{application_id}"
        )

        keyboard.button(
            text="❌ Отклонить",
            callback_data=f"reject:{application_id}"
        )

        await message.answer(
            f"🔔 Заявка №{application_id}\n\n"
            f"👤 Клиент: {client_name}\n"
            f"📝 Проблема:\n{problem}",
            reply_markup=keyboard.as_markup()
        )

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "Привет! Опиши свою проблему подробно, "
        "и я передам её мастеру."
    )


@dp.message(F.text)
async def receive_problem(message: Message):
    client_id = message.from_user.id
    client_name = message.from_user.full_name
    client_username = message.from_user.username
    problem = message.text

    application_id = database.add_application(
        client_id,
        client_name,
        client_username,
        problem
    )



    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text="✅ Взять заказ",
        callback_data=f"accept:{application_id}"
    )

    keyboard.button(
        text="❌ Отклонить",
        callback_data=f"reject:{application_id}"
    )

    await bot.send_message(
        MASTER_ID,
        f"🔔 Новая заявка!\n\n"
        f"👤 Клиент: {client_name}\n"
        f"📝 Проблема:\n{problem}",
        reply_markup=keyboard.as_markup()
    )

    await message.answer(
        "✅ Ваша заявка отправлена мастеру. Ожидайте ответа."
    )


@dp.callback_query(F.data.startswith("accept:"))
async def accept_order(callback: CallbackQuery):
    application_id = int(callback.data.split(":")[1])

    application = database.get_application(application_id)

    if application is None:
        await callback.answer("Заявка не найдена.")
        return

    client_id, client_name, client_username, _ = application

    updated = database.update_application_status(
        application_id,
        "accepted"
    )

    if updated == 0:
        await callback.answer("Эта заявка уже обработана.")
        return

    master_username = callback.from_user.username

    if master_username:
        master_contact = f"@{master_username}"
    else:
        master_contact = f"Telegram ID: {callback.from_user.id}"

    if client_username:
        client_contact = f"@{client_username}"
    else:
        client_contact = f"Telegram ID: {client_id}"

    await bot.send_message(
        client_id,
        "✅ Мастер готов выполнить вашу заявку!\n\n"
        f"📞 Контакт мастера: {master_contact}"
    )

    await callback.message.answer(
        f"✅ Заказ клиента {client_name} принят!\n\n"
        f"📞 Контакт клиента: {client_contact}"
    )

    await callback.message.edit_reply_markup(reply_markup=None)

    await callback.answer("Заказ принят!")

@dp.callback_query(F.data.startswith("reject:"))
async def reject_order(callback: CallbackQuery):
    application_id = int(callback.data.split(":")[1])

    application = database.get_application(application_id)

    if application is None:
        await callback.answer("Заявка не найдена.")
        return

    client_id, client_name, client_username, _ = application

    updated = database.update_application_status(
        application_id,
        "rejected"
    )

    if updated == 0:
        await callback.answer("Эта заявка уже обработана.")
        return

    await bot.send_message(
        client_id,
        "❌ К сожалению, мастер не готов помочь вам."
    )

    await callback.message.answer(
        f"❌ Заказ клиента {client_name} отклонён."
    )

    await callback.message.edit_reply_markup(reply_markup=None)

    await callback.answer("Заказ отклонён.")

async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())


