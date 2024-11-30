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
        self.database = 'db_project'
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

    def setup_ui(self):
        self.radioButton.toggled.connect(self.on_radio_selected)  # New order
        self.radioButton_2.toggled.connect(self.on_radio_selected)  # Track order
        self.radioButton_3.toggled.connect(self.on_radio_selected)  # Cart
        self.pushButton.clicked.connect(self.handle_selection)

    def handle_selection(self):
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

    def setup_ui(self):
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
        self.load_inventory()
        self.setup_connections()

    def load_inventory(self):
        db = DatabaseConnection()
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Inventory")
        
        self.inventoryTable.clearContents()
        for row_index, row_data in enumerate(cursor.fetchall()):
            self.inventoryTable.insertRow(row_index)
            for col_index, cell_data in enumerate(row_data):
                self.inventoryTable.setItem(row_index, col_index, 
                                         QTableWidgetItem(str(cell_data)))
        conn.close()

    def add_new_product(self):
        dialog = AddProductDialog()
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Add product logic here
            pass

    def edit_product(self):
        selected_row = self.inventoryTable.currentRow()
        if selected_row >= 0:
            product_id = self.inventoryTable.item(selected_row, 0).text()
            dialog = EditProductDialog(product_id)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                # Edit product logic here
                pass

# Order management screens
class UpdateOrderStatusScreen(QtWidgets.QMainWindow):
    def __init__(self, admin_email):
        super().__init__()
        uic.loadUi('screens/update order status.ui', self)
        self.admin_email = admin_email
        self.load_orders()
        self.setup_connections()

    def load_orders(self):
        db = DatabaseConnection()
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT o.Order_id, o.Order_status, o.Order_date, 
                   o.estimated_delivery_date, c.Customer_name
            FROM Orders o
            JOIN Customer c ON o.Customer_email = c.Customer_email
        """)
        
        self.ordersTable.clearContents()
        for row_index, row_data in enumerate(cursor.fetchall()):
            self.ordersTable.insertRow(row_index)
            for col_index, cell_data in enumerate(row_data):
                self.ordersTable.setItem(row_index, col_index, 
                                       QTableWidgetItem(str(cell_data)))
        conn.close()

    def update_order_status(self):
        selected_row = self.ordersTable.currentRow()
        if selected_row >= 0:
            order_id = self.ordersTable.item(selected_row, 0).text()
            new_status = self.statusCombo.currentText()
            
            db = DatabaseConnection()
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE Orders 
                SET Order_status = ?
                WHERE Order_id = ?
            """, (new_status, order_id))
            
            cursor.execute("""
                INSERT INTO Updates (Admin_email, Order_id)
                VALUES (?, ?)
            """, (self.admin_email, order_id))
            
            conn.commit()
            conn.close()
            self.load_orders()

# Customer order-related screens
class OrderScreen(QtWidgets.QMainWindow):
    def __init__(self, customer_email):
        super().__init__()
        uic.loadUi('screens/order.ui', self)
        self.customer_email = customer_email
        self.load_products()
        self.setup_connections()

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
        for row_index, row_data in enumerate(cursor.fetchall()):
            self.productsTable.insertRow(row_index)
            for col_index, cell_data in enumerate(row_data):
                self.productsTable.setItem(row_index, col_index, 
                                        QTableWidgetItem(str(cell_data)))
        conn.close()

    def add_to_cart(self):
        selected_row = self.productsTable.currentRow()
        if selected_row >= 0:
            product_id = self.productsTable.item(selected_row, 0).text()
            quantity = self.quantitySpinBox.value()
            
            db = DatabaseConnection()
            conn = db.get_connection()
            cursor = conn.cursor()
            
            # Add to cart logic here
            cursor.execute("""
                INSERT INTO Shopping_cart (Customer_email, Product_id, Quantity)
                VALUES (?, ?, ?)
            """, (self.customer_email, product_id, quantity))
            
            conn.commit()
            conn.close()

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
        self.load_cart()
        self.setup_connections()

    def load_cart(self):
        db = DatabaseConnection()
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT i.Product_id, i.Product_name, sc.Quantity, 
                   i.unit_price, (sc.Quantity * i.unit_price) as Total
            FROM Shopping_cart sc
            JOIN Inventory i ON sc.Product_id = i.Product_id
            WHERE sc.Customer_email = ?
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
                    DELETE FROM Shopping_cart 
                    WHERE Customer_email = ? AND Product_id = ?
                """, (self.customer_email, product_id))
                
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
        self.load_orders()

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
        
        self.ordersTable.clearContents()
        for row_index, row_data in enumerate(cursor.fetchall()):
            self.ordersTable.insertRow(row_index)
            for col_index, cell_data in enumerate(row_data):
                self.ordersTable.setItem(row_index, col_index, 
                                      QTableWidgetItem(str(cell_data)))
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
