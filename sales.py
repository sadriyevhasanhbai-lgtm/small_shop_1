import json
import os
from datetime import datetime

from inventory import find_product, parse_int, reduce_stock

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SALES_FILE = os.path.join(BASE_DIR, "sales.json")


def load_sales():
    """sales.json ni o'qiydi. Fayl yo'q yoki buzuq bo'lsa, bo'sh ro'yxat."""
    try:
        with open(SALES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []
    return data if isinstance(data, list) else []


def save_sales(sales):
    """Sotuvlar ro'yxatini sales.json ga yozadi."""
    with open(SALES_FILE, "w", encoding="utf-8") as f:
        json.dump(sales, f, indent=2, ensure_ascii=False)


def record_sale(products, sales, product_id, quantity_text):
    """Sotuvni qayd etadi: omborni kamaytiradi va tarixga yozadi. (ok, xabar) qaytaradi."""
    product_id = product_id.strip()
    product = find_product(products, product_id)
    if product is None:
        return False, "Mahsulot topilmadi."

    quantity = parse_int(quantity_text)
    if quantity is None or quantity <= 0:
        return False, "Miqdor musbat butun son bo'lishi kerak."

    ok, message = reduce_stock(products, product_id, quantity)
    if not ok:
        return False, message

    unit_price = product["price"]
    total = unit_price * quantity
    sales.append({
        "product_id": product_id,
        "name": product["name"],
        "quantity": quantity,
        "unit_price": unit_price,
        "total": total,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
    })
    save_sales(sales)
    return True, f"{quantity} dona {product['name']} sotildi: {total:,} UZS."


def total_revenue(sales):
    """Barcha sotuvlarning umumiy tushumi."""
    return sum(s["total"] for s in sales)


def average_sale_amount(sales):
    """Bir sotuvning o'rtacha summasi. Sotuvlar bo'lmasa None."""
    if not sales:
        return None
    return total_revenue(sales) / len(sales)


def best_selling_product(sales):
    """Miqdor bo'yicha eng ko'p sotilgan mahsulot. Sotuvlar bo'lmasa None."""
    quantities = {}
    names = {}
    for sale in sales:
        pid = sale["product_id"]
        quantities[pid] = quantities.get(pid, 0) + sale["quantity"]
        names[pid] = sale["name"]

    if not quantities:
        return None
    best_id = max(quantities, key=quantities.get)
    return {"name": names[best_id], "quantity": quantities[best_id]}


def low_stock_products(products, limit=5):
    """Omborda qoldig'i 'limit' yoki undan kam bo'lgan mahsulotlar."""
    return [p for p in products if p["stock"] <= limit]
