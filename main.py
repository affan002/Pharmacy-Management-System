from PyQt6 import QtWidgets, uic
from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import *
import sys
import pyodbc
from datetime import datetime, timedelta

# Database connection
class DatabaseConnection:
    def __init__(self):
        self.server = 'DESKTOP-G8KFEG6\\MYSQLSERVER1'
        self.database = 'final_project'
        self.connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={self.server};DATABASE={self.database};Trusted_Connection=yes;'

    def get_connection(self):
        try:
            conn = pyodbc.connect(self.connection_string)
            print("Database connection successful")
            return conn
        except Exception as e:
            print(f"Database connection failed: {e}")
            raise

# Base authentication class
class AuthenticationBase:
    def verify_credentials(self, email, password, is_admin=False):
        try:
            db = DatabaseConnection()
            conn = db.get_connection()
            cursor = conn.cursor()
            
            # Fix the column names in the query to match the database schema
            if is_admin:
                query = """
                    SELECT * FROM Admin 
                    WHERE Admin_email = ? AND password = ?
                """
            else:
                query = """
                    SELECT * FROM Customer 
                    WHERE Customer_email = ? AND password = ?
                """
            
            cursor.execute(query, (email, password))
            result = cursor.fetchone()
            
            # Debug print
            print(f"Query result: {result}")
            
            conn.close()
            return result is not None  # Return True if credentials are valid
        except Exception as e:
            print(f"Database error: {e}")
            return False

# Login screen classes
class CustomerLogin(QtWidgets.QMainWindow, AuthenticationBase):
    def __init__(self):
        super().__init__()
        uic.loadUi('screens/customerlogin.ui', self)
        self.pushButton_2.clicked.connect(self.handle_login)  # Login button
        self.pushButton.clicked.connect(self.open_create_account)  # Create account button

    def handle_login(self):
        email = self.lineEdit.text().strip()
        password = self.lineEdit_2.text().strip()
        
        if not email or not password:
            QMessageBox.warning(self, "Error", "Please enter both email and password")
            return
            
        try:
            is_valid = self.verify_credentials(email, password)
            if is_valid:
                self.customer_dashboard = CustomerDashboard(email)
                self.customer_dashboard.show()
                self.close()
            else:
                QMessageBox.warning(self, "Error", "Invalid email or password")
                self.lineEdit_2.clear()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Login failed: {str(e)}")

    def open_create_account(self):
        self.create_account = CreateAccount()
        self.create_account.show()
        self.close()

class AdminLogin(QtWidgets.QMainWindow, AuthenticationBase):
    def __init__(self):
        super().__init__()
        uic.loadUi('screens/adminlogin.ui', self)
        self.pushButton.clicked.connect(self.handle_login)

    def handle_login(self):
        email = self.lineEdit.text().strip()
        password = self.lineEdit_2.text().strip()
        
        if not email or not password:
            QMessageBox.warning(self, "Error", "Please enter both email and password")
            return
            
        try:
            is_valid = self.verify_credentials(email, password, is_admin=True)
            if is_valid:
                self.admin_dashboard = AdminDashboard(email)
                self.admin_dashboard.show()
                self.close()
            else:
                QMessageBox.warning(self, "Error", "Invalid email or password")
                self.lineEdit_2.clear()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Login failed: {str(e)}")

# Customer dashboard and related classes
class CustomerDashboard(QtWidgets.QMainWindow):
    def __init__(self, customer_email):
        super().__init__()
        uic.loadUi('screens/customermain.ui', self)
        self.customer_email = customer_email
        self.setup_ui()
    
    def get_customer_details(self, customer_email):
        db = DatabaseConnection()
        conn = db.get_connection()
        cursor = conn.cursor()

        # Query to get customer name
        query_name = "SELECT Customer_name FROM Customer WHERE Customer_email = ?"
        cursor.execute(query_name, (customer_email,))
        customer_name = cursor.fetchone()
        if customer_name:
            self.lineEdit.setText(customer_name[0])  # Set customer name
        else:   
            self.lineEdit.setText("Not found")
        
        query_address = "SELECT Address FROM Customer WHERE Customer_email = ?"
        cursor.execute(query_address, (customer_email,))
        customer_address = cursor.fetchone()
        if customer_address:
            self.lineEdit_2.setText(customer_address[0])
        else:
            self.lineEdit_2.setText("Not found")

        cursor.close()
        conn.close()

    def setup_ui(self):

        self.get_customer_details(self.customer_email)

        self.radioButton.toggled.connect(self.on_radio_selected)  # New order
        self.radioButton_2.toggled.connect(self.on_radio_selected)  # Track order
        self.radioButton_3.toggled.connect(self.on_radio_selected)  # Cart
        self.pushButton.clicked.connect(self.handle_selection)

    def handle_selection(self):

        # Update customer details in the database
        new_name = self.lineEdit.text().strip()
        new_address = self.lineEdit_2.text().strip()

        try:
            db = DatabaseConnection()
            conn = db.get_connection()
            cursor = conn.cursor()

            # Update query
            update_query = "UPDATE Customer SET Customer_name = ?, Address = ? WHERE Customer_email = ?"
            cursor.execute(update_query, (new_name, new_address, self.customer_email))
            conn.commit()

            cursor.close()
            conn.close()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update customer details: {str(e)}")
        
        if self.radioButton.isChecked():
            self.order_screen = OrderScreen(self.customer_email)
            self.order_screen.show()
        elif self.radioButton_2.isChecked():
            self.tracking_screen = OrderTrackingScreen(self.customer_email)
            self.tracking_screen.show()
        elif self.radioButton_3.isChecked():
            self.cart_screen = CartScreen(self.customer_email)
            self.cart_screen.show()

    def on_radio_selected(self):
        # Enable selection button when any radio is selected
        self.pushButton.setEnabled(True)

# Admin dashboard and related classes
class AdminDashboard(QtWidgets.QMainWindow):
    def __init__(self, admin_email):
        super().__init__()
        uic.loadUi('screens/admin_main_screen.ui', self)
        self.admin_email = admin_email
        self.setup_ui()

    # Assuming you have a method to get the database connection
    def get_admin_details(self, admin_email):
        db = DatabaseConnection()
        conn = db.get_connection()
        cursor = conn.cursor()

        # Query to get admin name
        query_name = "SELECT Admin_name FROM Admin WHERE Admin_email = ?"
        cursor.execute(query_name, (admin_email,))
        admin_name = cursor.fetchone()
        if admin_name:
            self.lineEdit.setText(admin_name[0])  # Set admin name
        else:
            self.lineEdit.setText("Not found")
        self.lineEdit.setReadOnly(True)  # Disable editing

        # Query to get admin job title
        query_title = "SELECT Job_title FROM Admin WHERE Admin_email = ?"
        cursor.execute(query_title, (admin_email,))
        admin_title = cursor.fetchone()
        if admin_title:
            self.lineEdit_2.setText(admin_title[0])  # Set admin title
        else:
            self.lineEdit_2.setText("Not found")
        self.lineEdit_2.setReadOnly(True)  # Disable editing

        # Close the cursor and connection
        cursor.close()
        conn.close()

    def setup_ui(self):

        self.get_admin_details(self.admin_email)
        
        self.radioButton.toggled.connect(self.on_radio_selected)  # Update order status
        self.radioButton_2.toggled.connect(self.on_radio_selected)  # Update inventory
        self.pushButton.clicked.connect(self.handle_selection)

    def handle_selection(self):
        if self.radioButton.isChecked():
            self.order_status_screen = UpdateOrderStatusScreen(self.admin_email)
            self.order_status_screen.show()
        elif self.radioButton_2.isChecked():
            self.inventory_screen = UpdateInventoryScreen(self.admin_email)
            self.inventory_screen.show()

    def on_radio_selected(self):
        # Enable selection button when any radio is selected
        self.pushButton.setEnabled(True)

# Inventory management screens
class UpdateInventoryScreen(QtWidgets.QMainWindow):
    def __init__(self, admin_email):
        super().__init__()
        uic.loadUi('screens/update inventory.ui', self)
        self.admin_email = admin_email
        self.setup_ui()
        self.load_inventory()

    def setup_ui(self):
        # Setup table properties
        self.tableWidget.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tableWidget.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        
        # Connect buttons
        self.pushButton.clicked.connect(self.add_new_product)  # Add new product
        self.pushButton_2.clicked.connect(self.delete_product)  # Delete product
        self.pushButton_3.clicked.connect(self.close)  # OK/Close button

    def load_inventory(self):
        db = DatabaseConnection()
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Inventory")
        
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(0)
        
        for row_index, row_data in enumerate(cursor.fetchall()):
            self.tableWidget.insertRow(row_index)
            for col_index, cell_data in enumerate(row_data):
                self.tableWidget.setItem(row_index, col_index, 
                                    QTableWidgetItem(str(cell_data)))
        conn.close()

    def add_new_product(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New Product")
        dialog.setModal(True)
        
        # Create form layout
        layout = QFormLayout(dialog)
        
        # Add input fields
        name_input = QLineEdit()
        qty_input = QSpinBox()
        qty_input.setMaximum(1000)
        price_input = QDoubleSpinBox()
        price_input.setMaximum(10000.00)
        category_input = QLineEdit()
        desc_input = QTextEdit()
        exp_date_input = QDateEdit()
        exp_date_input.setCalendarPopup(True)
        exp_date_input.setDate(QDate.currentDate().addYears(1))
        
        # Add fields to layout
        layout.addRow("Product Name:", name_input)
        layout.addRow("Quantity:", qty_input)
        layout.addRow("Unit Price:", price_input)
        layout.addRow("Category:", category_input)
        layout.addRow("Description:", desc_input)
        layout.addRow("Expiration Date:", exp_date_input)
        
        # Add buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                db = DatabaseConnection()
                conn = db.get_connection()
                cursor = conn.cursor()
                
                # First insert the product
                cursor.execute("""
                    INSERT INTO Inventory (Product_name, quantity_in_stock, description, 
                                        unit_price, category, expiration_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    name_input.text(),
                    qty_input.value(),
                    desc_input.toPlainText(),
                    price_input.value(),
                    category_input.text(),
                    exp_date_input.date().toString("yyyy-MM-dd")
                ))
                
                # Get the ID using a separate SELECT statement
                cursor.execute("SELECT IDENT_CURRENT('Inventory')")
                product_id = cursor.fetchone()[0]
                
                # Then create the management relationship using the obtained ID
                cursor.execute("""
                    INSERT INTO Manages (Admin_email, Product_id)
                    VALUES (?, ?)
                """, (self.admin_email, int(product_id)))
                
                conn.commit()
                conn.close()
                
                self.load_inventory()  # Refresh the table
                QMessageBox.information(self, "Success", "Product added successfully")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add product: {str(e)}")

    def delete_product(self):
        selected_row = self.tableWidget.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a product to delete")
            return
            
        product_id = self.tableWidget.item(selected_row, 0).text()
        product_name = self.tableWidget.item(selected_row, 1).text()
        
        reply = QMessageBox.question(self, "Confirm Delete",
                                   f"Are you sure you want to delete {product_name}?",
                                   QMessageBox.StandardButton.Yes | 
                                   QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                db = DatabaseConnection()
                conn = db.get_connection()
                cursor = conn.cursor()
                
                # Delete related records first
                cursor.execute("DELETE FROM Manages WHERE Product_id = ?", (product_id,))
                cursor.execute("DELETE FROM Inventory WHERE Product_id = ?", (product_id,))
                
                conn.commit()
                conn.close()
                
                self.load_inventory()  # Refresh the table
                QMessageBox.information(self, "Success", "Product deleted successfully")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete product: {str(e)}")

# Order management screens
class UpdateOrderStatusScreen(QtWidgets.QMainWindow):
    def __init__(self, admin_email):
        super().__init__()
        uic.loadUi('screens/update order status.ui', self)
        self.admin_email = admin_email
        self.setup_ui()
        self.load_orders()

    def setup_ui(self):
        # Set up status combo box options
        self.comboBox.addItems(['Pending', 'Processing', 'Shipped', 'Delivered'])
        # Connect buttons
        self.pushButton.clicked.connect(self.update_order_status)  # OK button
        # Setup date picker
        self.dateEdit.setCalendarPopup(True)
        self.dateEdit.setDate(QDate.currentDate().addDays(2))  # Default to 2 days from now
        # Setup table widget
        self.tableWidget.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tableWidget.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.tableWidget.itemSelectionChanged.connect(self.on_order_selected)

    def on_order_selected(self):
        selected_row = self.tableWidget.currentRow()
        if selected_row >= 0:
            # Update fields with selected order details
            order_id = self.tableWidget.item(selected_row, 0).text()
            status = self.tableWidget.item(selected_row, 1).text()
            delivery_date = self.tableWidget.item(selected_row, 3).text()
            
            self.lineEdit.setText(order_id)  # Order number
            self.comboBox.setCurrentText(status)  # Current status
            try:
                # Convert delivery date string to QDate
                date = QDate.fromString(delivery_date, "yyyy-MM-dd")
                self.dateEdit.setDate(date)
            except:
                self.dateEdit.setDate(QDate.currentDate().addDays(2))

    def load_orders(self):
        db = DatabaseConnection()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT o.Order_id, o.Order_status, o.Order_date, 
                   o.estimated_delivery_date, c.Customer_name,
                   i.Product_name, isc.item_quantity, i.unit_price,
                   i.description, i.expiration_date
            FROM Orders o
            JOIN Customer c ON o.Customer_email = c.Customer_email
            JOIN Shopping_cart sc ON o.Order_id = sc.OrderID
            JOIN Inventory_to_Shopping_Cart isc ON sc.shopping_cart_ID = isc.shopping_cart_ID
            JOIN Inventory i ON isc.product_ID = i.Product_id
        """)
        
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(0)
        for row_index, row_data in enumerate(cursor.fetchall()):
            self.tableWidget.insertRow(row_index)
            for col_index, cell_data in enumerate(row_data):
                self.tableWidget.setItem(row_index, col_index, 
                                       QTableWidgetItem(str(cell_data)))
        conn.close()

    def update_order_status(self):
        order_id = self.lineEdit.text()
        new_status = self.comboBox.currentText()
        new_delivery_date = self.dateEdit.date().toString("yyyy-MM-dd")
        
        if not order_id:
            QMessageBox.warning(self, "Error", "Please select an order first")
            return
            
        try:
            db = DatabaseConnection()
            conn = db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE Orders 
                SET Order_status = ?, estimated_delivery_date = ?
                WHERE Order_id = ?
            """, (new_status, new_delivery_date, order_id))
            
            cursor.execute("""
                INSERT INTO Updates (Admin_email, Order_id)
                VALUES (?, ?)
            """, (self.admin_email, order_id))
            
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, "Success", "Order status updated successfully")
            self.load_orders()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update order: {str(e)}")

# Customer order-related screens
class OrderScreen(QtWidgets.QMainWindow):
    def __init__(self, customer_email):
        super().__init__()
        uic.loadUi('screens/order.ui', self)
        self.customer_email = customer_email
        # Remove this line since productsTable already exists from the UI
        # self.productsTable = self.tableWidget
        
        # Add quantity spinbox
        self.quantitySpinBox = QSpinBox(self)
        self.quantitySpinBox.setMinimum(1)
        self.quantitySpinBox.setMaximum(100)
        self.quantitySpinBox.setGeometry(430, 320, 50, 21)
        
        self.setup_connections()
        self.load_products()  # Move this after setup is complete

    def setup_connections(self):
        self.pushButton.clicked.connect(self.search_products)  # Search button
        self.pushButton_2.clicked.connect(self.add_to_cart)  # Add to cart button
        self.pushButton_3.clicked.connect(self.view_cart)  # View cart button

    def view_cart(self):
        self.cart_screen = CartScreen(self.customer_email)
        self.cart_screen.show()

    def load_products(self):
        db = DatabaseConnection()
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Inventory WHERE quantity_in_stock > 0")
        
        self.productsTable.clearContents()
        self.productsTable.setRowCount(0)  # Reset row count
        
        for row_index, row_data in enumerate(cursor.fetchall()):
            self.productsTable.insertRow(row_index)
            # Set serial number in first column
            self.productsTable.setItem(row_index, 0, 
                                     QTableWidgetItem(str(row_index + 1)))
            # Add product data starting from column 1
            for col_index, cell_data in enumerate(row_data):
                self.productsTable.setItem(row_index, col_index + 1, 
                                         QTableWidgetItem(str(cell_data)))
        conn.close()
    
    def add_to_cart(self):
        selected_row = self.productsTable.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Error", "Please select a product")
            return
            
        conn = None
        try:
            # Adjust column indices to account for serial number column
            product_id = self.productsTable.item(selected_row, 1).text()  # Column 1 instead of 0
            requested_quantity = self.quantitySpinBox.value()
            available_quantity = int(self.productsTable.item(selected_row, 3).text())  # Column 3 instead of 2
            unit_price = float(self.productsTable.item(selected_row, 5).text())  # Column 5 instead of 4
            
            if requested_quantity > available_quantity:
                QMessageBox.warning(self, "Error", f"Only {available_quantity} items available")
                return
                
            db = DatabaseConnection()
            conn = db.get_connection()
            cursor = conn.cursor()
            
            # Start transaction
            cursor.execute("BEGIN TRANSACTION")
            
            # Check for existing cart
            cart_id = cursor.execute("""
                SELECT sc.shopping_cart_ID 
                FROM Shopping_cart sc
                RIGHT OUTER JOIN Orders o ON sc.OrderID = o.Order_id
                WHERE o.Order_id IS NULL AND o.Customer_email = ?
            """, (self.customer_email,))
            
            
            
            if not cart_id:
                # Create new cart if none exists
                cursor.execute("""
                    INSERT INTO Shopping_cart (OrderID) VALUES (NULL);
                    SELECT SCOPE_IDENTITY();
                """)
                cart_id = cursor.fetchone()[0]
           
            
            # Check if product already in cart
            cursor.execute("""
                SELECT item_quantity 
                FROM Inventory_to_Shopping_Cart 
                WHERE shopping_cart_ID = ? AND product_ID = ?
            """, (cart_id, product_id))
            
            existing_item = cursor.fetchone()
            
            if existing_item:
                # Update quantity if product exists
                new_quantity = existing_item[0] + requested_quantity
                cursor.execute("""
                    UPDATE Inventory_to_Shopping_Cart 
                    SET item_quantity = ?, Price = ? 
                    WHERE shopping_cart_ID = ? AND product_ID = ?
                """, (new_quantity, unit_price * new_quantity, cart_id, product_id))
            else:
                # Add new item to cart
                cursor.execute("""
                    INSERT INTO Inventory_to_Shopping_Cart 
                    (product_ID, shopping_cart_ID, item_quantity, Price)
                    VALUES (?, ?, ?, ?)
                """, (product_id, cart_id, requested_quantity, unit_price * requested_quantity))
            
            # Update inventory quantity
            cursor.execute("""
                UPDATE Inventory 
                SET quantity_in_stock = quantity_in_stock - ? 
                WHERE Product_id = ?
            """, (requested_quantity, product_id))
            
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, "Success", "Item added to cart")
            self.load_products()  # Refresh product list
            
        except Exception as e:
            if conn:
                conn.rollback()
                conn.close()
            QMessageBox.critical(self, "Error", f"Failed to add item: {str(e)}")

    def search_products(self):
        search_text = self.lineEdit.text().strip()
        if search_text:
            db = DatabaseConnection()
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM Inventory 
                WHERE quantity_in_stock > 0 
                AND (Product_name LIKE ? OR description LIKE ? OR category LIKE ?)
            """, (f'%{search_text}%', f'%{search_text}%', f'%{search_text}%'))
            
            self.productsTable.clearContents()
            self.productsTable.setRowCount(0)
            
            for row_index, row_data in enumerate(cursor.fetchall()):
                self.productsTable.insertRow(row_index)
                for col_index, cell_data in enumerate(row_data):
                    self.productsTable.setItem(row_index, col_index, 
                                            QTableWidgetItem(str(cell_data)))
            conn.close()

class CartScreen(QtWidgets.QMainWindow):
    def __init__(self, customer_email):
        super().__init__()
        uic.loadUi('screens/cart.ui', self)
        self.customer_email = customer_email
         # Add this line to map the widget
        self.load_cart()
        self.setup_connections()

    def load_cart(self):
        db = DatabaseConnection()
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT i.Product_id, i.Product_name, isc.item_quantity, 
                   i.unit_price, (isc.item_quantity * i.unit_price) as Total
            FROM Shopping_cart sc
            JOIN Inventory_to_Shopping_Cart isc ON sc.shopping_cart_ID = isc.shopping_cart_ID
            JOIN Inventory i ON isc.product_ID = i.Product_id
            JOIN Orders o ON sc.OrderID = o.Order_id
            WHERE o.Customer_email = ?
        """, (self.customer_email,))
        
        self.cartTable.clearContents()
        for row_index, row_data in enumerate(cursor.fetchall()):
            self.cartTable.insertRow(row_index)
            for col_index, cell_data in enumerate(row_data):
                self.cartTable.setItem(row_index, col_index, 
                                    QTableWidgetItem(str(cell_data)))
        conn.close()

    def setup_connections(self):
        self.pushButton.clicked.connect(self.delete_item)  # Delete button
        self.pushButton_2.clicked.connect(self.proceed_to_checkout)  # Proceed to payment button

    def proceed_to_checkout(self):
        self.payment_screen = PaymentScreen(self.customer_email)
        self.payment_screen.show()

    def delete_item(self):
        selected_row = self.cartTable.currentRow()
        if selected_row >= 0:
            product_id = self.cartTable.item(selected_row, 0).text()
            
            try:
                db = DatabaseConnection()
                conn = db.get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM Inventory_to_Shopping_Cart 
                    WHERE product_ID = ? AND shopping_cart_ID IN (
                        SELECT sc.shopping_cart_ID 
                        FROM Shopping_cart sc
                        JOIN Orders o ON sc.OrderID = o.Order_id
                        WHERE o.Customer_email = ?
                    )
                """, (product_id, self.customer_email))
                
                conn.commit()
                conn.close()
                
                self.load_cart()  # Refresh cart view
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete item: {str(e)}")

class OrderTrackingScreen(QtWidgets.QMainWindow):
    def __init__(self, customer_email):
        super().__init__()
        uic.loadUi('screens/orderstatus.ui', self)
        self.customer_email = customer_email
        self.setup_ui()
        self.load_orders()

    def setup_ui(self):
        # Match widgets from orderstatus.ui
        self.pushButton.clicked.connect(self.close)  # Close button
        self.lineEdit.setEnabled(False)  # Order ID field
        self.lineEdit_2.setEnabled(False)  # Expected delivery date field
        self.comboBox.setEnabled(False)  # Status combobox

    def load_orders(self):
        db = DatabaseConnection()
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT o.Order_id, o.Order_status, o.Order_date, 
                   o.estimated_delivery_date
            FROM Orders o
            WHERE o.Customer_email = ?
        """, (self.customer_email,))

        result = cursor.fetchone()
        if result:
            # Display the most recent order details
            self.lineEdit.setText(str(result[0]))  # Order ID
            self.comboBox.addItem(str(result[1]))  # Status
            self.lineEdit_2.setText(str(result[3]))  # Expected delivery date

        conn.close()

# Add this class before the main() function
class RoleSelection(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('screens/select_role.ui', self)
        self.setup_ui()

    def setup_ui(self):
        # Connect radio buttons and proceed button
        self.radioButton.toggled.connect(self.on_role_selected)  # Customer radio
        self.radioButton_2.toggled.connect(self.on_role_selected)  # Admin radio
        self.pushButton.clicked.connect(self.proceed_to_login)  # Proceed button
        self.pushButton.setEnabled(False)

    def on_role_selected(self):
        self.pushButton.setEnabled(True)

    def proceed_to_login(self):
        if self.radioButton.isChecked():  # Customer
            self.login_screen = CustomerLogin()
            self.login_screen.show()
            self.close()
        elif self.radioButton_2.isChecked():  # Admin
            self.login_screen = AdminLogin()
            self.login_screen.show()
            self.close()

# Add CreateAccount class
class CreateAccount(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('screens/create_account.ui', self)
        self.pushButton.clicked.connect(self.handle_create_account)

    def handle_create_account(self):
        email = self.lineEdit.text().strip()
        password = self.lineEdit_2.text().strip()
        confirm_password = self.lineEdit_3.text().strip()
        full_name = self.lineEdit_4.text().strip()
        address = self.lineEdit_5.text().strip()
        contact = self.lineEdit_6.text().strip()

        if not all([email, password, confirm_password, full_name, address, contact]):
            QMessageBox.warning(self, "Error", "Please fill all fields")
            return

        if password != confirm_password:
            QMessageBox.warning(self, "Error", "Passwords do not match")
            return

        try:
            db = DatabaseConnection()
            conn = db.get_connection()
            cursor = conn.cursor()
            
            # Check if email already exists
            cursor.execute("SELECT * FROM Customer WHERE Customer_email = ?", (email,))
            if cursor.fetchone():
                QMessageBox.warning(self, "Error", "Email already registered")
                return

            # Insert new customer
            cursor.execute("""
                INSERT INTO Customer (Customer_email, Customer_name, password, Address, Contact_no)
                VALUES (?, ?, ?, ?, ?)
            """, (email, full_name, password, address, contact))
            
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Success", "Account created successfully")
            self.login_screen = CustomerLogin()
            self.login_screen.show()
            self.close()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create account: {str(e)}")

# Add PaymentScreen class
class PaymentScreen(QtWidgets.QMainWindow):
    def __init__(self, customer_email):
        super().__init__()
        uic.loadUi('screens/payment.ui', self)
        self.customer_email = customer_email
        self.setup_ui()

    def setup_ui(self):
        self.pushButton.clicked.connect(self.process_payment)
        self.load_payment_details()

    def load_payment_details(self):
        # Load order total from cart
        db = DatabaseConnection()
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT SUM(i.unit_price * sc.Quantity) as Total
            FROM Shopping_cart sc
            JOIN Inventory i ON sc.Product_id = i.Product_id
            WHERE sc.Customer_email = ?
        """, (self.customer_email,))
        
        total = cursor.fetchone()[0]
        self.lineEdit_3.setText(str(total))  # Total amount
        self.lineEdit_3.setEnabled(False)  # Make read-only
        conn.close()

    def process_payment(self):
        try:
            db = DatabaseConnection()
            conn = db.get_connection()
            cursor = conn.cursor()
            
            # Create payment record
            total = float(self.lineEdit_3.text())
            cursor.execute("INSERT INTO Payment (Total_amount) VALUES (?)", (total,))
            cursor.execute("SELECT @@IDENTITY")  # Get last inserted payment ID
            payment_id = cursor.fetchone()[0]
            
            # Create order
            cursor.execute("""
                INSERT INTO Orders (Order_status, Order_date, estimated_delivery_date, Payment_id, Customer_email)
                VALUES (?, GETDATE(), DATEADD(day, 2, GETDATE()), ?, ?)
            """, ('Pending', payment_id, self.customer_email))
            
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, "Success", "Payment processed successfully")
            self.close()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Payment failed: {str(e)}")

def main():
    app = QApplication(sys.argv)
    window = RoleSelection()  # Start with role selection
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()




