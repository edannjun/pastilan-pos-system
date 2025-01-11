import sqlite3

# Create the database and table
def create_menu_db():
    """
    Creates the database and the menu_items table if they do not exist.
    Adds an image_path column to store the path of images associated with menu items.
    """
    conn = sqlite3.connect("menu.db")  # Connect to the database (it will create if it doesn't exist)
    cursor = conn.cursor()

    # Create a table for storing menu items with an image_path column
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS menu_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            image_path TEXT
        )
    ''')

    conn.commit()
    conn.close()

# Load menu items from the database
def load_menu_items():
    """
    Loads all menu items from the database, including their associated image paths.
    Returns:
        list of dict: Each dict contains the name, price, and image_path of a menu item.
    """
    conn = sqlite3.connect("menu.db")
    cursor = conn.cursor()

    # Fetch all items, including their image paths
    cursor.execute("SELECT name, price, image_path FROM menu_items")
    rows = cursor.fetchall()

    # Convert rows to a list of dictionaries
    menu_items = [{"name": row[0], "price": row[1], "image_path": row[2]} for row in rows]

    conn.close()
    return menu_items

# Add a menu item to the database
def add_menu_item(name, price, image_path):
    """
    Adds a new menu item to the database, including the image path.
    Args:
        name (str): Name of the menu item.
        price (float): Price of the menu item.
        image_path (str): Path to the image associated with the menu item.
    """
    conn = sqlite3.connect("menu.db")
    cursor = conn.cursor()

    # Insert the menu item along with its image path
    cursor.execute("INSERT INTO menu_items (name, price, image_path) VALUES (?, ?, ?)", (name, price, image_path))

    conn.commit()
    conn.close()

# Remove a menu item from the database
def remove_menu_item(name):
    """
    Removes a menu item from the database by its name.
    Args:
        name (str): Name of the menu item to be removed.
    """
    conn = sqlite3.connect("menu.db")
    cursor = conn.cursor()

    # Delete the menu item with the given name
    cursor.execute("DELETE FROM menu_items WHERE name = ?", (name,))

    conn.commit()
    conn.close()
