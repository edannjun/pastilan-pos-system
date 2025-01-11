import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QWidget, QGridLayout, QLineEdit, QDialog, QMessageBox, QScrollArea, QCalendarWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QIcon
from menu_db import create_menu_db, load_menu_items, add_menu_item, remove_menu_item
from inventory_db import create_checkout_db, add_order
from inventory_viewer import get_inventory_by_date
from PyQt6.QtWidgets import QFileDialog
import shutil

class ManageMenuDialog(QDialog):
    def __init__(self, menu_items, update_menu_callback):
        super().__init__()
        self.setWindowTitle("Manage Menu")
        self.menu_items = menu_items
        self.update_menu_callback = update_menu_callback
        self.image_path = None  # To store the uploaded image path

        layout = QVBoxLayout()

        # Upload Image Section
        self.upload_image_button = QPushButton("Upload Image")
        self.upload_image_button.clicked.connect(self.upload_image)
        layout.addWidget(self.upload_image_button)

        self.image_preview = QLabel("No image uploaded")
        self.image_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_preview.setStyleSheet("border: 1px solid gray; padding: 5px;")
        layout.addWidget(self.image_preview)

        # Add Item Section
        self.item_name_input = QLineEdit()
        self.item_name_input.setPlaceholderText("Enter item name")
        self.item_price_input = QLineEdit()
        self.item_price_input.setPlaceholderText("Enter item price")

        add_item_button = QPushButton("Add Item")
        add_item_button.clicked.connect(self.add_item)

        layout.addWidget(self.item_name_input)
        layout.addWidget(self.item_price_input)
        layout.addWidget(add_item_button)

        # Remove Item Section
        self.item_remove_input = QLineEdit()
        self.item_remove_input.setPlaceholderText("Enter item name to remove")
        remove_item_button = QPushButton("Remove Item")
        remove_item_button.clicked.connect(self.remove_item)

        layout.addWidget(self.item_remove_input)
        layout.addWidget(remove_item_button)

        self.setLayout(layout)

    def upload_image(self):
        """Handles uploading an image to the res folder."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)")
        if not file_path:
            return  # User canceled the dialog

        base_path = os.path.dirname(__file__)  # Current script directory
        res_folder = os.path.join(base_path, "../res")
        os.makedirs(res_folder, exist_ok=True)

        try:
            file_name = os.path.basename(file_path)
            destination_path = os.path.join(res_folder, file_name)
            shutil.copy(file_path, destination_path)
            self.image_path = destination_path  # Store the path of the uploaded image

            # Update the preview label with the uploaded image
            pixmap = QPixmap(destination_path).scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio)
            self.image_preview.setPixmap(pixmap)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to upload image: {str(e)}")

    def add_item(self):
        """Adds a new item with an uploaded or default image to the menu."""
        name = self.item_name_input.text()
        try:
            price = float(self.item_price_input.text())
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Price must be a number!")
            return

        # Use default image if no image is uploaded
        if not self.image_path:
            base_path = os.path.dirname(__file__)  # Current script directory
            res_folder = os.path.join(base_path, "../res")
            self.image_path = os.path.join(res_folder, "no-image.png")

            # Verify that the default image exists
            if not os.path.exists(self.image_path):
                QMessageBox.critical(self, "Error", "Default image (no-image.png) is missing!")
                return

        if name:
            # Embed the image path with the menu item
            add_menu_item(name, price, self.image_path)
            QMessageBox.information(self, "Item Added", f"{name} added to menu!")
            self.update_menu_callback()
            self.item_name_input.clear()
            self.item_price_input.clear()
            self.image_preview.clear()
            self.image_preview.setText("No image uploaded")
            self.image_path = None
        else:
            QMessageBox.warning(self, "Invalid Input", "Item name cannot be empty!")

    def remove_item(self):
        """Removes an item from the menu."""
        name = self.item_remove_input.text()
        if name in [item["name"] for item in self.menu_items]:
            remove_menu_item(name)
            QMessageBox.information(self, "Item Removed", f"{name} removed from menu!")
            self.update_menu_callback()
            self.item_remove_input.clear()
        else:
            QMessageBox.warning(self, "Not Found", f"{name} not found in menu!")



class ViewInventoryDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("View Inventory")

        self.resize(800, 600)

        layout = QVBoxLayout()

        # Add a label and calendar
        self.date_label = QLabel("Select Date:")
        layout.addWidget(self.date_label)

        self.calendar = QCalendarWidget()
        self.calendar.selectionChanged.connect(self.update_table)
        layout.addWidget(self.calendar)

        # Add a table widget to show inventory data
        self.table = QTableWidget(0, 4)  # Exclude the date column
        self.table.setHorizontalHeaderLabels(["ID", "Item Name", "Quantity", "Total Price"])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        # Add a label to show the total sum of the prices
        self.total_label = QLabel("Total Amount: ₱0.00")
        self.total_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.total_label)

        self.setLayout(layout)
        self.update_table()  # Load the initial data

    def update_table(self):
        """Updates the inventory table based on the selected date."""
        selected_date = self.calendar.selectedDate().toString("yyyy-MM-dd")

        # Fetch filtered orders using the backend function
        orders = get_inventory_by_date(selected_date)

        # Populate the table
        self.table.setRowCount(0)  # Clear existing rows
        total_amount = 0
        for row_number, row_data in enumerate(orders):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

            total_amount += row_data[3]

        self.total_label.setText(f"Total Amount: ₱{total_amount:.2f}")



class POSMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pastilan POS System")
        self.setGeometry(100, 100, 1200, 700)

        create_checkout_db()  # Initialize the checkout database
        self.menu_items = load_menu_items()
        
        # Determine the icon path
        if getattr(sys, 'frozen', False):  # If the app is frozen (compiled)
            base_path = os.path.dirname(sys.executable)
        else:  # If running as a script
            base_path = os.path.dirname(__file__)

        image_path = os.path.join(base_path, "..", "res", "icon.png")


        # Set the application icon
        self.setWindowIcon(QIcon(image_path))  # Replace with your icon file path

        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        
        # Sidebar (Left Panel)
        sidebar = QVBoxLayout()
        sidebar.setSpacing(10)
        
        # Determine the base path
        if getattr(sys, 'frozen', False):  # If the app is frozen (compiled)
            base_path = os.path.dirname(sys.executable)
        else:  # If running as a script
            base_path = os.path.dirname(__file__)

        # Set the image path relative to the base path
        image_logo_path = os.path.join(base_path, "..", "res", "logo.png")

        # Check if the file exists before loading the image
        if not os.path.exists(image_logo_path):
            print(f"Error: The image file does not exist at path {image_logo_path}")
        else:
            # Create the label and load the image
            image_label = QLabel()
            pixmap = QPixmap(image_logo_path)

            if pixmap.isNull():
                print(f"Failed to load image: {image_logo_path}")
            
            else:
                # Scale the pixmap and set it
                pixmap = pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio)
                image_label.setPixmap(pixmap)
                image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

                # Assuming you have a layout or container to add this image label to
                sidebar.addWidget(image_label)

        # Add the "Manage Menu" button below the image
        manage_menu_button = QPushButton("Manage Menu")
        manage_menu_button.clicked.connect(self.open_manage_menu)
        sidebar.addWidget(manage_menu_button)

        # Add the "View Inventory" button below "Manage Menu"
        view_inventory_button = QPushButton("View Inventory")
        view_inventory_button.clicked.connect(self.open_view_inventory)
        sidebar.addWidget(view_inventory_button)

        main_layout.addLayout(sidebar)

        # Order Summary (Center Panel)
        order_summary = QVBoxLayout()
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Item", "Qty", "Price", "Total", "Actions"])
        self.table.setColumnWidth(0, 150)
        self.table.setColumnWidth(1, 85)
        self.table.setColumnWidth(2, 100)
        self.table.setColumnWidth(3, 98)
        self.table.setColumnWidth(4, 150)
        order_summary.addWidget(self.table)
        
        # Total Label
        self.total_label = QLabel("Total: ₱0.00")
        self.total_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.total_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-right: 10px;")
        order_summary.addWidget(self.total_label)


        checkout_btn = QPushButton("Submit")
        checkout_btn.clicked.connect(self.checkout)  # Connect to checkout functionality
        checkout_btn.setFixedSize(800,40)
        checkout_btn.setStyleSheet("background-color: #32CD32; color: white;")
        order_summary.addWidget(checkout_btn)
        main_layout.addLayout(order_summary)

        # Product Grid (Right Panel with Scroll Area)
        self.product_grid = QGridLayout()
        self.product_grid.setSpacing(5)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        grid_container = QWidget()
        grid_container.setLayout(self.product_grid)

        scroll_area.setWidget(grid_container)

        right_panel = QVBoxLayout()
        right_panel.addWidget(scroll_area)
        main_layout.addLayout(right_panel)

        # Set proportions for the panels
        main_layout.setStretch(0, 1)  # Sidebar
        main_layout.setStretch(1, 5)  # Order Summary
        main_layout.setStretch(2, 3)  # Product Grid

        self.setCentralWidget(main_widget)
        self.update_product_grid()

    def open_manage_menu(self):
        """Opens the Manage Menu dialog."""
        dialog = ManageMenuDialog(self.menu_items, self.update_product_grid)
        dialog.exec()

    def open_view_inventory(self):
        """Opens the View Inventory dialog."""
        dialog = ViewInventoryDialog()
        dialog.exec()

    def update_product_grid(self):
        """Updates the product grid dynamically based on the menu items."""
        for i in reversed(range(self.product_grid.count())):
            self.product_grid.itemAt(i).widget().deleteLater()

        for index, product in enumerate(self.menu_items):
            row = index // 2
            col = index % 2

            # Add the item image
            image_label = QLabel()
            if product["image_path"] and os.path.exists(product["image_path"]):
                pixmap = QPixmap(product["image_path"]).scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio)
                image_label.setPixmap(pixmap)
            else:
                # Use a default placeholder if the image is missing
                default_image_path = os.path.join(os.path.dirname(__file__), "../res/no-image.png")
                pixmap = QPixmap(default_image_path).scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio)
                image_label.setPixmap(pixmap)
            image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # Add the item name
            name_label = QLabel(product["name"])
            name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            name_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 5px;")
            item_container = QVBoxLayout()

            # Add the components to the container
            item_container.addWidget(image_label)
            item_container.addWidget(name_label)
            item_container.setSpacing(10)

             # Create a widget for the container and add it to the grid
            item_widget = QWidget()
            item_widget.setLayout(item_container)
            self.product_grid.addWidget(item_widget, row, col)

            add_button = QPushButton("Add to Order")
            add_button.setStyleSheet("background-color: green; color: white;")
            add_button.setMinimumSize(120, 40)
            add_button.clicked.connect(lambda _, p=product: self.add_to_order(p))

            item_container.addWidget(add_button)
            item_container.setSpacing(5)

            item_widget = QWidget()
            item_widget.setLayout(item_container)
            self.product_grid.addWidget(item_widget, row, col)

    def update_total(self):
        """Calculates and updates the total price displayed in the center panel."""
        total_price = 0.0
        for row in range(self.table.rowCount()):
            total_item_price = float(self.table.item(row, 3).text().replace("₱", ""))
            total_price += total_item_price

        self.total_label.setText(f"Total: ₱{total_price:.2f}")

    def add_to_order(self, product):
        item_name = product["name"]
        item_price = product["price"]

        for row in range(self.table.rowCount()):
            if self.table.item(row, 0).text() == item_name:
                current_qty = int(self.table.item(row, 1).text())
                self.table.setItem(row, 1, QTableWidgetItem(str(current_qty + 1)))
                new_total = (current_qty + 1) * item_price
                self.table.setItem(row, 3, QTableWidgetItem(f"₱{new_total:.2f}"))
                self.update_total()  # Update the total after adding
                return

        row_position = self.table.rowCount()
        self.table.insertRow(row_position)
        self.table.setItem(row_position, 0, QTableWidgetItem(item_name))
        self.table.setItem(row_position, 1, QTableWidgetItem("1"))
        self.table.setItem(row_position, 2, QTableWidgetItem(f"₱{item_price:.2f}"))
        self.table.setItem(row_position, 3, QTableWidgetItem(f"₱{item_price:.2f}"))

        subtract_button = QPushButton("-")
        subtract_button.setStyleSheet("background-color: red; color: white; border: none;")
        subtract_button.clicked.connect(lambda _, r=row_position: self.subtract_qty(r, item_price))
        self.table.setCellWidget(row_position, 4, subtract_button)

        self.update_total()

    def subtract_qty(self, row, item_price):
        current_qty = int(self.table.item(row, 1).text())
        if current_qty > 1:
            new_qty = current_qty - 1
            self.table.setItem(row, 1, QTableWidgetItem(str(new_qty)))
            new_total = new_qty * item_price
            self.table.setItem(row, 3, QTableWidgetItem(f"₱{new_total:.2f}"))
        else:
            self.table.removeRow(row)

        self.update_total()

    def checkout(self):
        """Handles checkout process by storing orders in the database."""
        row_count = self.table.rowCount()

        if row_count == 0:
            QMessageBox.warning(self, "Empty Order", "No items in the order to check out!")
            return

        # Loop through the table to get order details
        for row in range(row_count):
            item_name = self.table.item(row, 0).text()
            quantity = int(self.table.item(row, 1).text())
            price = float(self.table.item(row, 2).text().replace("₱", ""))
            total = float(self.table.item(row, 3).text().replace("₱", ""))

            # Add order to the checkout database
            add_order(item_name, quantity, price, total)

        # Clear the table after checkout
        self.table.setRowCount(0)
        QMessageBox.information(self, "Order Checked Out", "Order has been successfully checked out!")


if __name__ == "__main__":
    create_menu_db()

    app = QApplication(sys.argv)
    window = POSMainWindow()
    window.show()
    sys.exit(app.exec())
