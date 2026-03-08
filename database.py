import sqlite3

conn = sqlite3.connect("bot.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    phone TEXT,
    orders_count INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    kit TEXT,
    status TEXT
)
""")

conn.commit()


def add_user(user_id, phone):
    cursor.execute(
        "INSERT OR IGNORE INTO users (user_id, phone) VALUES (?, ?)",
        (user_id, phone)
    )
    conn.commit()


def add_order(user_id, kit):
    cursor.execute(
        "INSERT INTO orders (user_id, kit, status) VALUES (?, ?, ?)",
        (user_id, kit, "новый")
    )
    conn.commit()


def get_orders():
    cursor.execute("SELECT * FROM orders ORDER BY id DESC")
    return cursor.fetchall()


def get_users():
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()