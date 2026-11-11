import json
import os

import numpy as np

# Fayl yo'li shu .py fayl turgan papkaga bog'langan,
# shuning uchun dasturni qayerdan ishga tushirsangiz ham bir xil ishlaydi.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PRODUCTS_FILE = os.path.join(BASE_DIR, "products.json")


def parse_int(text):
    """Matnni butun songa aylantiradi. Bo'lmasa None qaytaradi."""
    text = text.strip()
    if "_" in text:          # Python "1_000" ni ham son deb qabul qiladi, biz yo'q
        return None
    try:
        return int(text)
    except ValueError:
        return None


def load_products():
    """products.json ni o'qiydi. Fayl yo'q yoki buzuq bo'lsa, bo'sh ro'yxat."""
    try:
        with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []
    return data if isinstance(data, list) else []


def save_products(products):
    """Mahsulotlar ro'yxatini products.json ga yozadi."""
    with open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
        json.dump(products, f, indent=2, ensure_ascii=False)


def find_product(products, product_id):
    """ID bo'yicha mahsulotni topadi. Topilmasa None."""
    for product in products:
        if product["id"] == product_id:
            return product
    return None


def add_product(products, product_id, name, price_text, stock_text):
    """Yangi mahsulot qo'shadi. (ok, xabar) qaytaradi."""
    product_id = product_id.strip()
    name = name.strip()

    if product_id == "":
        return False, "ID bo'sh bo'lmasligi kerak."
    if find_product(products, product_id) is not None:
        return False, "Bu ID allaqachon mavjud."
    if name == "":
        return False, "Nom bo'sh bo'lmasligi kerak."

    price = parse_int(price_text)
    if price is None or price <= 0:
        return False, "Narx musbat butun son bo'lishi kerak."

    stock = parse_int(stock_text)
    if stock is None or stock < 0:
        return False, "Ombordagi soni 0 yoki undan katta butun son bo'lishi kerak."

    products.append({"id": product_id, "name": name, "price": price, "stock": stock})
    save_products(products)
    return True, "Mahsulot qo'shildi."


def search_products(products, query):
    """Nom (qismi bo'yicha, harf kattaligiga qaramay) yoki ID (aniq) bo'yicha qidiradi."""
    query = query.strip()
    if query == "":
        return []
    q = query.lower()
    return [p for p in products if q in p["name"].lower() or p["id"] == query]


def restock_product(products, product_id, quantity_text):
    """Mavjud mahsulot soniga qo'shadi. (ok, xabar) qaytaradi."""
    product = find_product(products, product_id.strip())
    if product is None:
        return False, "Mahsulot topilmadi."

    quantity = parse_int(quantity_text)
    if quantity is None or quantity <= 0:
        return False, "Miqdor musbat butun son bo'lishi kerak."

    product["stock"] += quantity
    save_products(products)
    return True, f"Zaxira to'ldirildi. Yangi qoldiq: {product['stock']} dona."


def reduce_stock(products, product_id, quantity):
    """Sotuv uchun ombordan ayiradi. Yetarli bo'lmasa hech narsa o'zgarmaydi."""
    product = find_product(products, product_id)
    if product is None:
        return False, "Mahsulot topilmadi."
    if quantity <= 0:
        return False, "Miqdor musbat bo'lishi kerak."
    if quantity > product["stock"]:
        return False, f"Omborda faqat {product['stock']} dona bor."

    product["stock"] -= quantity
    save_products(products)
    return True, "Ombor yangilandi."


def total_inventory_value(products):
    """Ombordagi hamma tovarning umumiy qiymati (NumPy bilan)."""
    if not products:
        return 0
    prices = np.array([p["price"] for p in products], dtype=np.int64)
    stocks = np.array([p["stock"] for p in products], dtype=np.int64)
    return int(np.sum(prices * stocks))