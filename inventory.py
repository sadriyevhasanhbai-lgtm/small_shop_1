import json
import os

import numpy as np
from pydantic import ValidationError

from models import Product, ProductList

# Fayl yo'li shu .py fayl turgan papkaga bog'langan,
# shuning uchun dasturni qayerdan ishga tushirsangiz ham bir xil ishlaydi.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PRODUCTS_FILE = os.path.join(BASE_DIR, "products.json")


def parse_int(text: str) -> int | None:
    """Matnni butun songa aylantiradi. Bo'lmasa None qaytaradi."""
    text = text.strip()
    # Python "1_000" ni ham son deb qabul qiladi, biz yo'q.
    if "_" in text:
        return None
    try:
        return int(text)
    except ValueError:
        return None


def load_products() -> list[Product]:
    """products.json ni o'qiydi. Fayl yo'q yoki buzuq bo'lsa, bo'sh ro'yxat."""
    try:
        with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []
    try:
        return ProductList.model_validate(data).root
    except ValidationError:
        return []


def save_products(products: list[Product]) -> None:
    """Mahsulotlar ro'yxatini products.json ga yozadi."""
    with open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
        json.dump(
            [p.model_dump() for p in products],
            f,
            indent=2,
            ensure_ascii=False,
        )


def find_product(products: list[Product], product_id: str) -> Product | None:
    """ID bo'yicha mahsulotni topadi. Topilmasa None."""
    for product in products:
        if product.id == product_id:
            return product
    return None


def add_product(
    products: list[Product],
    product_id: str,
    name: str,
    price_text: str,
    stock_text: str,
) -> tuple[bool, str]:
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
        return False, (
            "Ombordagi soni 0 yoki undan katta butun son bo'lishi kerak."
        )

    try:
        product = Product(id=product_id, name=name, price=price, stock=stock)
    except ValidationError:
        return False, "Mahsulot ma'lumotlari noto'g'ri."

    products.append(product)
    save_products(products)
    return True, "Mahsulot qo'shildi."


def search_products(products: list[Product], query: str) -> list[Product]:
    """Nom (qismi bo'yicha, harf kattaligiga qaramay) yoki ID (aniq) bo'yicha
    qidiradi."""
    query = query.strip()
    if query == "":
        return []
    q = query.lower()
    return [p for p in products if q in p.name.lower() or p.id == query]


def restock_product(
    products: list[Product],
    product_id: str,
    quantity_text: str,
) -> tuple[bool, str]:
    """Mavjud mahsulot soniga qo'shadi. (ok, xabar) qaytaradi."""
    product = find_product(products, product_id.strip())
    if product is None:
        return False, "Mahsulot topilmadi."

    quantity = parse_int(quantity_text)
    if quantity is None or quantity <= 0:
        return False, "Miqdor musbat butun son bo'lishi kerak."

    product.stock += quantity
    save_products(products)
    return True, f"Zaxira to'ldirildi. Yangi qoldiq: {product.stock} dona."


def reduce_stock(
    products: list[Product],
    product_id: str,
    quantity: int,
) -> tuple[bool, str]:
    """Sotuv uchun ombordan ayiradi.

    Yetarli bo'lmasa hech narsa o'zgarmaydi.
    """
    product = find_product(products, product_id)
    if product is None:
        return False, "Mahsulot topilmadi."
    if quantity <= 0:
        return False, "Miqdor musbat bo'lishi kerak."
    if quantity > product.stock:
        return False, f"Omborda faqat {product.stock} dona bor."

    product.stock -= quantity
    save_products(products)
    return True, "Ombor yangilandi."


def total_inventory_value(products: list[Product]) -> int:
    """Ombordagi hamma tovarning umumiy qiymati (NumPy bilan)."""
    if not products:
        return 0
    prices = np.array([p.price for p in products], dtype=np.int64)
    stocks = np.array([p.stock for p in products], dtype=np.int64)
    return int(np.sum(prices * stocks))
