# Small Shop

A simple terminal-based inventory and sales manager for a small shop.
The application is written in Python, uses **Pydantic v2** for data
validation and **NumPy** for inventory value calculations, and stores
all data in local JSON files.

## Features

- Add new products with a unique ID, name, price, and stock quantity
- List all products in a formatted table
- Search products by name (case-insensitive substring) or exact ID
- Restock existing products
- Record sales with automatic stock deduction
- View sales history
- Reports:
  - total revenue
  - average sale amount
  - best-selling product by quantity
  - total inventory value (calculated with NumPy)
  - low-stock products (5 units or fewer)
- Persistent JSON storage with schema validation on load and save

## Requirements

- Python 3.11 or newer (developed and tested on Python 3.12)
- Dependencies from `requirements.txt`:
  - `numpy`
  - `pydantic` (v2)

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running the application

```bash
python main.py
```

The application starts an interactive menu:

```text
=== Kichik do'kon ===
1. Mahsulot qo'shish
2. Mahsulotlarni ko'rish
3. Mahsulot qidirish
4. Zaxirani to'ldirish
5. Sotuv yozish
6. Sotuvlar tarixi
7. Hisobotlar
0. Chiqish
```

The user interface is in Uzbek. Enter the number of the desired action
and follow the prompts. Use `0` to exit. `Ctrl+C` or `Ctrl+D` also
stops the program safely.

## Project structure

```text
.
├── main.py          # Interactive menu and program entry point
├── inventory.py     # Product loading, saving, search, and stock logic
├── sales.py         # Sale recording, history, and reports
├── models.py        # Pydantic models and validation rules
├── requirements.txt # Runtime dependencies
├── products.json    # Product data (created on first write, git-ignored)
└── sales.json       # Sales history (created on first write, git-ignored)
```

File paths are resolved relative to the project directory, so the
application works regardless of the directory it is launched from.
No environment variables or external configuration are required.

## Data storage

### `products.json`

A JSON array of products:

```json
[
  {
    "id": "1",
    "name": "Notebook",
    "price": 15000,
    "stock": 7
  }
]
```

| Field   | Type   | Rules                          |
|---------|--------|--------------------------------|
| `id`    | string | non-empty, must be unique      |
| `name`  | string | non-empty                      |
| `price` | int    | greater than 0                 |
| `stock` | int    | 0 or greater                   |

### `sales.json`

A JSON array of completed sales:

```json
[
  {
    "product_id": "1",
    "name": "Notebook",
    "quantity": 3,
    "unit_price": 15000,
    "total": 45000,
    "time": "2026-11-11 17:56"
  }
]
```

| Field        | Type   | Rules                                |
|--------------|--------|--------------------------------------|
| `product_id` | string | non-empty                            |
| `name`       | string | non-empty                            |
| `quantity`   | int    | greater than 0                       |
| `unit_price` | int    | greater than 0                       |
| `total`      | int    | must equal `unit_price * quantity`   |
| `time`       | string | local time in `YYYY-MM-DD HH:MM`     |

Both files are created automatically the first time data is saved.
If a file is missing or contains invalid JSON, the application starts
with an empty list. Leading and trailing whitespace in string fields
is stripped by Pydantic.

## Business rules

- Product IDs must be unique.
- Prices and restock quantities must be positive integers.
- A sale is rejected if the requested quantity exceeds available stock;
  in that case, stock and sales history remain unchanged.
- Recording a sale reduces stock and appends an entry to `sales.json`.
- Low-stock report lists products with `stock <= 5`.
- The best-selling product is determined by total quantity sold, not
  by revenue.

## Code style

The code follows [PEP 8](https://peps.python.org/pep-0008/):

- 4-space indentation and a maximum line length of 79 characters
- `snake_case` for functions and variables, `PascalCase` for classes
- grouped imports (standard library, third-party, local)
- type annotations on function signatures
- two blank lines between top-level definitions

Style can be checked with:

```bash
pip install pycodestyle
python -m pycodestyle --max-line-length=79 *.py
```

## Limitations

- Single-user command-line application; no concurrent access handling.
- Sales history is append-only — sales cannot be edited or deleted.
- Monetary values are stored as plain integers (UZS), without decimal
  precision or currency conversion.
