import sqlite3
from datetime import datetime

# Create the database and table for storing orders
def create_checkout_db():
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    # Create a table for storing order details if it doesn't already exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            total REAL NOT NULL,
            date TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

# Add an order to the database
def add_order(item_name, quantity, price, total):
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    # Get the current date and time
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Check if the item already exists
    cursor.execute('''SELECT id, quantity, total FROM orders WHERE item_name = ?''', (item_name,))
    existing_order = cursor.fetchone()

    if existing_order:
        # If the item exists, update the quantity and total
        existing_quantity = existing_order[1]
        existing_total = existing_order[2]

        new_quantity = existing_quantity + quantity
        new_total = existing_total + total

        cursor.execute('''UPDATE orders SET quantity = ?, total = ? WHERE id = ?''',
                       (new_quantity, new_total, existing_order[0]))
    else:
        # If the item doesn't exist, insert a new order
        cursor.execute('''INSERT INTO orders (item_name, quantity, price, total, date)
                          VALUES (?, ?, ?, ?, ?)''',
                       (item_name, quantity, price, total, date))

    conn.commit()
    conn.close()


# Retrieve all orders from the database, optionally sorted by date
def get_all_orders():
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM orders ORDER BY date DESC")
    orders = cursor.fetchall()

    conn.close()
    return orders
