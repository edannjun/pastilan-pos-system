import sqlite3

def get_inventory_by_date(selected_date):
    """
    Fetch inventory data from the database for the specified date.

    :param selected_date: Date string in "YYYY-MM-DD" format.
    :return: List of inventory rows (excluding the date column).
    """
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, item_name, quantity, total FROM orders WHERE date(date) = ?", (selected_date,)
    )
    orders = cursor.fetchall()
    conn.close()
    return orders
