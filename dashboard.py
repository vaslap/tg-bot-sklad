import matplotlib.pyplot as plt

def generate_dashboard_text(products):
    total_quantity = sum(p["quantity"] for p in products.values())
    total_reserved = sum(p["reserved"] for p in products.values())
    
    text = f"📊 Сводка по складу\n\n"
    text += f"📦 Всего товаров: {total_quantity} шт.\n"
    text += f"🔒 Всего в резерве: {total_reserved} шт.\n"
    text += f"✅ Доступно к отгрузке: {total_quantity - total_reserved} шт.\n"
    text += f"📋 Количество позиций: {len(products)}\n\n"
    text += "Детали:\n"
    
    for sku, p in products.items():
        available = p["quantity"] - p["reserved"]
        text += f"• {sku}: {p['name']} — {p['quantity']} шт. (резерв: {p['reserved']}, доступно: {available})\n"
    
    return text