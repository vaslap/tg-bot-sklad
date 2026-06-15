import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# ===== НАСТРОЙКИ =====
TOKEN = "8899033755:AAG78mH7Vf7AtRORbtehWnQg_w2U20h04ms"
logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ===== БАЗА ДАННЫХ (словарь, потом заменим на SQLite) =====
products = {
    "ТОВ-001": {"name": "Смартфон X", "quantity": 150, "reserved": 30},
    "ТОВ-002": {"name": "Наушники Pro", "quantity": 200, "reserved": 15},
    "ТОВ-003": {"name": "Зарядное устройство", "quantity": 300, "reserved": 45},
}

# ===== ОБЩИЕ ФУНКЦИИ =====
def get_available(sku):
    """Возвращает доступное количество товара"""
    if sku in products:
        return products[sku]["quantity"] - products[sku]["reserved"]
    return 0

# ===== КОМАНДЫ =====
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 **Бот для управления складом WMS**\n\n"
        "📋 **Доступные команды:**\n"
        "/check `<артикул>` — проверить остатки\n"
        "/reserve `<артикул>` `<кол-во>` — зарезервировать\n"
        "/receipt `<артикул>` `<кол-во>` — приход товара\n"
        "/ship `<артикул>` `<кол-во>` — отгрузка\n"
        "/inventory `<артикул>` `<кол-во>` — инвентаризация\n"
        "/dashboard — сводка по складу\n"
        "/help — помощь\n\n"
        "📌 **Пример:** `/check ТОВ-001`",
        parse_mode="Markdown"
    )

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await cmd_start(message)

@dp.message(Command("check"))
async def cmd_check(message: types.Message):
    args = message.text.split()
    if len(args) < 2:
        await message.answer("❌ Укажи артикул. Пример: `/check ТОВ-001`", parse_mode="Markdown")
        return
    
    sku = args[1].upper()
    
    if sku in products:
        p = products[sku]
        available = p["quantity"] - p["reserved"]
        await message.answer(
            f"📊 **{p['name']}**\n"
            f"📦 Остаток: {p['quantity']} шт.\n"
            f"🔒 Резерв: {p['reserved']} шт.\n"
            f"✅ Доступно: {available} шт.",
            parse_mode="Markdown"
        )
    else:
        await message.answer(f"❌ Товар с артикулом `{sku}` не найден", parse_mode="Markdown")

@dp.message(Command("reserve"))
async def cmd_reserve(message: types.Message):
    args = message.text.split()
    if len(args) < 3:
        await message.answer("❌ Пример: `/reserve ТОВ-001 10`", parse_mode="Markdown")
        return
    
    sku = args[1].upper()
    try:
        qty = int(args[2])
    except ValueError:
        await message.answer("❌ Количество должно быть числом")
        return
    
    if sku not in products:
        await message.answer(f"❌ Товар `{sku}` не найден", parse_mode="Markdown")
        return
    
    available = get_available(sku)
    if qty <= 0:
        await message.answer("❌ Количество должно быть больше 0")
        return
    
    if qty > available:
        await message.answer(f"❌ Недостаточно товара. Доступно: {available} шт.")
        return
    
    products[sku]["reserved"] += qty
    await message.answer(f"✅ **Зарезервировано** {qty} шт. товара `{sku}`\n\nТеперь доступно: {get_available(sku)} шт.", parse_mode="Markdown")

@dp.message(Command("receipt"))
async def cmd_receipt(message: types.Message):
    args = message.text.split()
    if len(args) < 3:
        await message.answer("❌ Пример: `/receipt ТОВ-001 100`", parse_mode="Markdown")
        return
    
    sku = args[1].upper()
    try:
        qty = int(args[2])
    except ValueError:
        await message.answer("❌ Количество должно быть числом")
        return
    
    if qty <= 0:
        await message.answer("❌ Количество должно быть больше 0")
        return
    
    if sku in products:
        products[sku]["quantity"] += qty
    else:
        products[sku] = {"name": f"Новый товар {sku}", "quantity": qty, "reserved": 0}
    
    await message.answer(f"✅ **Оприходовано** {qty} шт. товара `{sku}`\n\nНовый остаток: {products[sku]['quantity']} шт.", parse_mode="Markdown")

@dp.message(Command("ship"))
async def cmd_ship(message: types.Message):
    args = message.text.split()
    if len(args) < 3:
        await message.answer("❌ Пример: `/ship ТОВ-001 10`", parse_mode="Markdown")
        return
    
    sku = args[1].upper()
    try:
        qty = int(args[2])
    except ValueError:
        await message.answer("❌ Количество должно быть числом")
        return
    
    if sku not in products:
        await message.answer(f"❌ Товар `{sku}` не найден", parse_mode="Markdown")
        return
    
    available = get_available(sku)
    if qty <= 0:
        await message.answer("❌ Количество должно быть больше 0")
        return
    
    if qty > available:
        await message.answer(f"❌ Недостаточно товара. Доступно: {available} шт.")
        return
    
    p = products[sku]
    # Сначала списываем из резерва
    if qty <= p["reserved"]:
        p["reserved"] -= qty
    else:
        qty_from_stock = qty - p["reserved"]
        p["reserved"] = 0
        p["quantity"] -= qty_from_stock
    
    await message.answer(f"✅ **Отгружено** {qty} шт. товара `{sku}`\n\nОстаток: {p['quantity']} шт., Резерв: {p['reserved']} шт.", parse_mode="Markdown")

@dp.message(Command("inventory"))
async def cmd_inventory(message: types.Message):
    args = message.text.split()
    if len(args) < 3:
        await message.answer("❌ Пример: `/inventory ТОВ-001 145`", parse_mode="Markdown")
        return
    
    sku = args[1].upper()
    try:
        actual_qty = int(args[2])
    except ValueError:
        await message.answer("❌ Количество должно быть числом")
        return
    
    if sku not in products:
        await message.answer(f"❌ Товар `{sku}` не найден", parse_mode="Markdown")
        return
    
    old_qty = products[sku]["quantity"]
    diff = actual_qty - old_qty
    
    products[sku]["quantity"] = actual_qty
    
    # Если фактическое количество меньше резерва — корректируем резерв
    if products[sku]["reserved"] > actual_qty:
        products[sku]["reserved"] = actual_qty
    
    if diff > 0:
        await message.answer(f"✅ **Инвентаризация** товара `{sku}`\n\n"
                            f"Было: {old_qty} шт.\n"
                            f"Стало: {actual_qty} шт.\n"
                            f"➕ Добавлено: {diff} шт.", parse_mode="Markdown")
    elif diff < 0:
        await message.answer(f"✅ **Инвентаризация** товара `{sku}`\n\n"
                            f"Было: {old_qty} шт.\n"
                            f"Стало: {actual_qty} шт.\n"
                            f"➖ Списано: {abs(diff)} шт.", parse_mode="Markdown")
    else:
        await message.answer(f"✅ **Инвентаризация** товара `{sku}`\n\n"
                            f"Расхождений нет. Остаток: {actual_qty} шт.", parse_mode="Markdown")

@dp.message(Command("dashboard"))
async def cmd_dashboard(message: types.Message):
    total_quantity = sum(p["quantity"] for p in products.values())
    total_reserved = sum(p["reserved"] for p in products.values())
    
    # Список товаров для детального отчёта
    items_list = []
    for sku, p in products.items():
        available = p["quantity"] - p["reserved"]
        items_list.append(f"• `{sku}`: {p['quantity']} шт. (резерв: {p['reserved']}, доступно: {available})")
    
    items_text = "\n".join(items_list) if items_list else "Нет товаров"
    
    await message.answer(
        f"📊 **Сводка по складу**\n\n"
        f"📦 **Всего товаров:** {total_quantity} шт.\n"
        f"🔒 **Всего в резерве:** {total_reserved} шт.\n"
        f"✅ **Доступно к отгрузке:** {total_quantity - total_reserved} шт.\n"
        f"📋 **Количество позиций:** {len(products)}\n\n"
        f"**Детали:**\n{items_text}",
        parse_mode="Markdown"
    )

# ===== ЗАПУСК =====
async def main():
    print("🚀 Бот для управления складом запущен!")
    print(f"📋 Доступно команд: /start, /check, /reserve, /receipt, /ship, /inventory, /dashboard")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())