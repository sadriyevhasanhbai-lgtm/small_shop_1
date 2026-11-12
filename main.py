import inventory
import sales as sales_module
 
 
def money(amount):
    return f"{amount:,} UZS"
 
 
def print_products(items):
    print(f"{'ID':<10}{'Nomi':<25}{'Narx':>16}{'Qoldiq':>10}")
    print("-" * 61)
    for p in items:
        print(f"{p['id']:<10}{p['name']:<25}{money(p['price']):>16}{p['stock']:>10}")
 
 
def menu_add(products):
    product_id = input("Mahsulot ID: ")
    name = input("Nomi: ")
    price = input("Narxi (UZS): ")
    stock = input("Ombordagi soni: ")
    ok, message = inventory.add_product(products, product_id, name, price, stock)
    print(message)
 
 
def menu_list(products):
    if not products:
        print("Ombor bo'sh. Avval mahsulot qo'shing.")
        return
    print_products(products)
 
 
def menu_search(products):
    if not products:
        print("Ombor bo'sh. Qidirish uchun mahsulot yo'q.")
        return
    query = input("Nom yoki ID: ")
    found = inventory.search_products(products, query)
    if not found:
        print("Hech narsa topilmadi.")
        return
    print_products(found)
 
 
def menu_restock(products):
    if not products:
        print("Ombor bo'sh. Avval mahsulot qo'shing.")
        return
    product_id = input("Mahsulot ID: ")
    quantity = input("Qo'shiladigan miqdor: ")
    ok, message = inventory.restock_product(products, product_id, quantity)
    print(message)
 
 
def menu_sale(products, sales):
    if not products:
        print("Ombor bo'sh. Sotish uchun mahsulot yo'q.")
        return
    product_id = input("Mahsulot ID: ")
    quantity = input("Miqdor: ")
    ok, message = sales_module.record_sale(products, sales, product_id, quantity)
    print(message)
 
 
def menu_history(sales):
    if not sales:
        print("Sotuvlar tarixi hozircha bo'sh.")
        return
    print(f"{'Mahsulot':<25}{'Miqdor':>8}{'Narx':>16}{'Jami':>18}")
    print("-" * 67)
    for s in sales:
        print(f"{s['name']:<25}{s['quantity']:>8}"
              f"{money(s['unit_price']):>16}{money(s['total']):>18}")
 
 
def menu_reports(products, sales):
    print("--- Hisobotlar ---")
    print(f"Umumiy tushum: {money(sales_module.total_revenue(sales))}")
 
    average = sales_module.average_sale_amount(sales)
    if average is None:
        print("O'rtacha sotuv: sotuvlar hali yo'q")
    else:
        print(f"O'rtacha sotuv: {average:,.0f} UZS")
 
    best = sales_module.best_selling_product(sales)
    if best is None:
        print("Eng ko'p sotilgan mahsulot: sotuvlar hali yo'q")
    else:
        print(f"Eng ko'p sotilgan mahsulot: {best['name']} ({best['quantity']} dona)")
 
    print(f"Ombordagi tovarlar qiymati: {money(inventory.total_inventory_value(products))}")
 
    low = sales_module.low_stock_products(products)
    if not low:
        print("Qoldig'i 5 yoki undan kam mahsulotlar: yo'q")
    else:
        print("Qoldig'i 5 yoki undan kam mahsulotlar:")
        print_products(low)
 
 
def main():
    products = inventory.load_products()
    sales = sales_module.load_sales()
 
    while True:
        print("\n=== Kichik do'kon ===")
        print("1. Mahsulot qo'shish")
        print("2. Mahsulotlarni ko'rish")
        print("3. Mahsulot qidirish")
        print("4. Zaxirani to'ldirish")
        print("5. Sotuv yozish")
        print("6. Sotuvlar tarixi")
        print("7. Hisobotlar")
        print("0. Chiqish")
        choice = input("Tanlang: ").strip()
 
        if choice == "1":
            menu_add(products)
        elif choice == "2":
            menu_list(products)
        elif choice == "3":
            menu_search(products)
        elif choice == "4":
            menu_restock(products)
        elif choice == "5":
            menu_sale(products, sales)
        elif choice == "6":
            menu_history(sales)
        elif choice == "7":
            menu_reports(products, sales)
        elif choice == "0":
            print("Xayr!")
            break
        else:
            print("Noto'g'ri tanlov. 0 dan 7 gacha raqam kiriting.")
 
 
if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nDastur to'xtatildi.")