import sqlite3

CUSTOMERS = [
    (1, "Customer One", "customer1@example.test", "1 Main Street, Austin, TX"),
    (2, "Customer Two", "canary2@example.test", "5 Pine Avenue, Houston, TX"),
]

# (id, customer_id, status, placed_at, total, ship_address, refund_amount)
ORDERS = [
    (101, 1, "placed",    "2026-10-30", 60.00, "1 Main Street, Austin, TX", None),
    (102, 1, "shipped",   "2026-10-25", 35.00, "1 Main Street, Austin, TX", None),
    (103, 1, "delivered", "2026-10-20", 80.00, "1 Main Street, Austin, TX", None),
    (104, 1, "delivered", "2026-09-01", 50.00, "1 Main Street, Austin, TX", None),
    (105, 1, "placed",    "2026-10-31", 25.00, "1 Main Street, Austin, TX", None),
    (106, 2, "delivered", "2026-10-22", 40.00, "9 Marker Road, Plano, TX", None),
    (107, 2, "placed",    "2026-10-31", 70.00, "77 Canary Lane, Dallas, TX", None),
    (108, 1, "cancelled", "2026-10-15", 30.00, "1 Main Street, Austin, TX", None),
]

# (order_id, sku, qty, price)
ORDER_ITEMS = [
    (101, "SKU-A", 2, 20.00), (101, "SKU-B", 1, 20.00),
    (102, "SKU-C", 1, 35.00),
    (103, "SKU-D", 2, 40.00),
    (104, "SKU-E", 1, 50.00),
    (105, "SKU-F", 1, 25.00),
    (106, "SKU-G", 1, 40.00),
    (107, "SKU-H", 1, 30.00), (107, "SKU-I", 2, 20.00),
    (108, "SKU-J", 1, 30.00),
]

def get_connection(db_path):
    connection = sqlite3.connect(db_path)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def create_tables(connection):
    connection.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            address TEXT NOT NULL
        )
    """)
    connection.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL REFERENCES customers(id),
            status TEXT NOT NULL CHECK (status IN ('placed', 'shipped', 'delivered', 'cancelled', 'refunded')),
            placed_at TEXT NOT NULL,
            total REAL NOT NULL,
            ship_address TEXT NOT NULL,
            refund_amount REAL
        )
    """)
    connection.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            order_id INTEGER NOT NULL REFERENCES orders(id),
            sku TEXT NOT NULL,
            qty INTEGER NOT NULL CHECK (qty > 0),
            price REAL NOT NULL
        )
    """)
    connection.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY,
            order_id INTEGER NOT NULL REFERENCES orders(id),
            text TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

def reset(connection):
    connection.execute("DROP TABLE IF EXISTS notes")
    connection.execute("DROP TABLE IF EXISTS order_items")
    connection.execute("DROP TABLE IF EXISTS orders")
    connection.execute("DROP TABLE IF EXISTS customers")
    create_tables(connection)
    connection.executemany(
        "INSERT INTO customers (id, name, email, address) VALUES (?, ?, ?, ?)",
        CUSTOMERS,
    )
    connection.executemany(
        "INSERT INTO orders (id, customer_id, status, placed_at, total, ship_address, refund_amount) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        ORDERS,
    )
    # your turn: the same pattern for order_item
    connection.executemany(
            "INSERT INTO order_items (order_id, sku, qty, price) VALUES (?, ?, ?, ?)",
            ORDER_ITEMS,
        )
    connection.commit()

def initialize_database(db_path):
    connection = None
    try:
        connection = get_connection(db_path)
        create_tables(connection)
    finally:
        if connection is not None:
            connection.close()
