import json
import os
from datetime import datetime

from pydantic import ValidationError

from inventory import find_product, parse_int, reduce_stock
from models import BestSeller, Product, Sale, SaleList

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SALES_FILE = os.path.join(BASE_DIR, "sales.json")


def load_sales() -> list[Sale]:
    """sales.json ni o'qiydi. Fayl yo'q yoki buzuq bo'lsa, bo'sh ro'yxat."""
    try:
        with open(SALES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []
    try:
        return SaleList.model_validate(data).root
    except ValidationError:
        return []


def save_sales(sales: list[Sale]) -> None:
    """Sotuvlar ro'yxatini sales.json ga yozadi."""
    with open(SALES_FILE, "w", encoding="utf-8") as f:
        json.dump(
            [s.model_dump() for s in sales],
            f,
            indent=2,
            ensure_ascii=False,
        )


def record_sale(
    products: list[Product],
    sales: list[Sale],
    product_id: str,
    quantity_text: str,
) -> tuple[bool, str]:
    """Sotuvni qayd etadi va tarixga yozadi. (ok, xabar) qaytaradi.

    Omborni kamaytiradi.
    """
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

    unit_price = product.price
    sale = Sale(
        product_id=product_id,
        name=product.name,
        quantity=quantity,
        unit_price=unit_price,
        total=unit_price * quantity,
        time=datetime.now().strftime("%Y-%m-%d %H:%M"),
    )
    sales.append(sale)
    save_sales(sales)
    return True, f"{quantity} dona {product.name} sotildi: {sale.total:,} UZS."


def total_revenue(sales: list[Sale]) -> int:
    """Barcha sotuvlarning umumiy tushumi."""
    return sum(s.total for s in sales)


def average_sale_amount(sales: list[Sale]) -> float | None:
    """Bir sotuvning o'rtacha summasi. Sotuvlar bo'lmasa None."""
    if not sales:
        return None
    return total_revenue(sales) / len(sales)


def best_selling_product(sales: list[Sale]) -> BestSeller | None:
    """Miqdor bo'yicha eng ko'p sotilgan mahsulot. Sotuvlar bo'lmasa None."""
    quantities: dict[str, int] = {}
    names: dict[str, str] = {}
    for sale in sales:
        pid = sale.product_id
        quantities[pid] = quantities.get(pid, 0) + sale.quantity
        names[pid] = sale.name

    if not quantities:
        return None
    best_id = max(quantities, key=quantities.get)
    return BestSeller(name=names[best_id], quantity=quantities[best_id])


def low_stock_products(
    products: list[Product],
    limit: int = 5,
) -> list[Product]:
    """Omborda qoldig'i 'limit' yoki undan kam bo'lgan mahsulotlar."""
    return [p for p in products if p.stock <= limit]
