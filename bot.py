import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv
from database import Database
from dashboard import generate_dashboard_text

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()
db = Database()

# Временное хранилище (для совместимости с dashboard)
products = {}

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("👋 Бот для управления складом\n\n/check <артикул> - проверка остатков")

@dp.message(Command("check"))
async def cmd_check(message: types.Message):
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Укажи артикул: /check ТОВ-001")
        return
    sku = args[1].upper()
    product = db.get_product(sku)
    if product:
        available = product["quantity"] - product["reserved"]
        await message.answer(f"{product['name']}\nОстаток: {product['quantity']}\nДоступно: {available}")
    else:
        await message.answer(f"Товар {sku} не найден")

@dp.message(Command("dashboard"))
async def cmd_dashboard(message: types.Message):
    # Загружаем данные из БД
    db.cursor.execute("SELECT sku, name, quantity, reserved FROM products")
    rows = db.cursor.fetchall()
    products_data = {row[0]: {"name": row[1], "quantity": row[2], "reserved": row[3]} for row in rows}
    text = generate_dashboard_text(products_data)
    await message.answer(text)

async def main():
    print("🚀 Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())