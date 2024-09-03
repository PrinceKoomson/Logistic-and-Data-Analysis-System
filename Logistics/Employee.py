import sys
import os
import sys
import os
import datetime
import math
import secrets
import string
import hashlib
import time
import threading
import math
from PyQt5.QtPrintSupport import QPrinter
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIntValidator, QPixmap, QTextDocument, QFont, QPdfWriter, QPainter
from PyQt5.QtCore import QDateTime, QDate, QTimer, Qt, QPointF, QRectF
from PyQt5.QtWidgets import QWidget, QApplication, QDialog, QStackedWidget, QTableWidget,  QAbstractItemView,  QToolButton, QWidget, QComboBox, QHBoxLayout, QVBoxLayout, QTableWidgetItem, QMessageBox, QLineEdit, QLabel, QFileDialog
from functools import partial
#from login import Loginpage
#import importlib
#DB connection
import mysql.connector as con
db = con.connect(host="localhost", user="root", password ="1234567890", database ="logisticsdb")
cursor = db.cursor()

cache = {}

def update_cache(key, value):
    """
    Update the cache with new data.
    """
    cache[key] = value
    print(f"Cache updated: {key} -> {value}")

def flush_cache_to_db():
    """
    Flush the cached data to the database using the existing connection.
    """
    global db, cursor
    try:
        if not cache:
            pass
            return

        # Ensure the database connection is still active
        if not db.is_connected():
            db.reconnect()
            cursor = db.cursor()

        for key, value in cache.items():
            # Update your database according to the cache data structure
            cursor.execute("UPDATE sales SET your_column_name = %s WHERE id = %s", (value, key))

        db.commit()
        print("Cache flushed to database.")

        # Clear the cache after flushing
        cache.clear()

    except con.Error as err:
        print(f"Error updating database: {err}")

def periodic_flush():
    """
    Periodically flush cache to database every 5 hours.
    """
    while True:
        time.sleep(5 * 3600)  # Sleep for 5 hours
        flush_cache_to_db()

# Start the periodic flushing thread
flush_thread = threading.Thread(target=periodic_flush, daemon=True)
flush_thread.start()



class EmpDboard(QDialog):
    def __init__(self):
        super(EmpDboard, self).__init__()
        main_dir = os.path.dirname(os.path.abspath(__file__))
        EmpUi = os.path.join(main_dir, 'Ui', 'EmpUI_2.ui')
        loadUi(EmpUi, self)
 # Set the window to full screen
        self.setWindowState(Qt.WindowFullScreen)

        #ProTable
        self.ProTable.setColumnWidth(0, 100)
        self.ProTable.setColumnWidth(1, 300)
        self.ProTable.setColumnWidth(2, 200)
        self.ProTable.setColumnWidth(3, 100)
        self.ProCombo.lineEdit().setPlaceholderText("--Search--")

        self.Uline = QLineEdit()
        self.Uline.setVisible(False)
        self.Bline = QLineEdit()
        self.Bline.setVisible(False)

        person = self.Uline.text()
        branch = self.Bline.text()
        self.EmpName.setText(person)
        self.BrName.setText(branch)

        comboque= "SELECT Product_name FROM Products"
        cursor.execute(comboque)
        products = cursor.fetchall()
        self.ProCombo.addItem(None)
        for item in products:
            self.ProCombo.addItem(item[0])
        self.ProCombo.completer().setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
        
        #def CartT(self):
        self.CartTable.setColumnWidth(0, 50)
        self.CartTable.setColumnWidth(1, 240)
        self.CartTable.setColumnWidth(2, 140)
        self.CartTable.setColumnWidth(3, 140)
        self.CartTable.setColumnWidth(4, 140)
        self.receipt.setColumnWidth(0, 30)
        self.receipt.setColumnWidth(1, 200)
        self.receipt.setColumnWidth(2, 80)
        self.receipt.setColumnWidth(3, 80)
        
        self.CartTable.setSelectionMode(QAbstractItemView.NoSelection)
        self.CartTable.setEditTriggers(QTableWidget.NoEditTriggers)
        self.ProTable.setSelectionMode(QAbstractItemView.NoSelection)
        self.ProTable.setEditTriggers(QTableWidget.NoEditTriggers)
        self.receipt.setSelectionMode(QAbstractItemView.NoSelection)
        self.receipt.setEditTriggers(QTableWidget.NoEditTriggers)
        
        self.receiptWid = self.CheckoutWid
        

        self.Qty.textChanged.connect(self.Stockcheck)
        
        #buttons

        self.ProFrame.show()
        self.ProDetails.show()
        self.CartTable.hide()
        self.CheckoutWid.hide()
        self.ProductsButton.setToolTip("products")
        self.ProductsButton.clicked.connect(self.Products)
        self.CartButton.clicked.connect(self.Cart)
        self.AddtoCartButton.clicked.connect(self.AddtoCart)
        self.QtyDec.clicked.connect(self.qtydec)
        self.QtyInc.clicked.connect(self.qtyinc)
        self.ConfirmOrder.clicked.connect(self.ConOrder)
        self.Qty.setValidator(QIntValidator(1, 10000))
        self.LogOutButton.clicked.connect(self.logout)

        self.Chdatime.setDateTime(QDateTime.currentDateTime())
        self.timer = QTimer(self)
        self.timer.timeout.connect(lambda:self.Chdatime.setDateTime(QDateTime.currentDateTime()))
        self.timer.start(1000)

        self.populateTable()
    
    def populateTable(self):
        query = "SELECT Product_ID, Product_Name FROM Products"
        cursor.execute(query)
        result = cursor.fetchall()
        #populating product table
        self.ProTable.setRowCount(0)
        for row_num, row_data in enumerate(result):
            self.ProTable.insertRow(row_num)
            minpricequery = "SELECT MIN(Price) FROM specificproducts WHERE Product_name = %s"
            cursor.execute(minpricequery, (row_data[1],))
            MinPrice = cursor.fetchone()[0]
            maxpricequery = "SELECT MAX(Price) FROM specificproducts WHERE Product_name = %s"
            cursor.execute(maxpricequery, (row_data[1],))
            MaxPrice = cursor.fetchone()[0]
            PriceRange = f"{MinPrice} - {MaxPrice}"
            for col_num, data in enumerate(row_data):
                self.ProTable.setItem(row_num, col_num, QTableWidgetItem(str(data)))
                
            self.ProTable.setItem(row_num, 2, QTableWidgetItem(str(PriceRange)))

            # Create a new button widget for each row
            View_button = QToolButton()
            View_button.setText("View")
            View_button.setToolTip("View product")
            View_button.setStyleSheet('border:none')
            View_button.setCursor(Qt.PointingHandCursor)
            
            button_widget = QWidget()
            button_layout = QHBoxLayout()
            button_layout.addWidget(View_button)
            button_layout.setContentsMargins(0, 0, 0, 0)
            button_widget.setLayout(button_layout)

            self.ProTable.setCellWidget(row_num, 3, button_widget)
            View_button.clicked.connect(partial(self.ProClicked, row_num))
        
    def ProClicked(self, row_num):
        # Get the row that was clicked
        self.DstorageBox.clear()
        self.DramBox.clear()
        row = row_num
        self.Qty.setText('1')
        send = self.sender()
        if send:
            product_name = self.ProTable.item(row, 1).text()

            # Fetch the minimum price
            pricequery = "SELECT MIN(Price) FROM specificproducts WHERE Product_name = %s"
            cursor.execute(pricequery, (product_name,))
            MinPrice = cursor.fetchone()[0]

            # Fetch the product details
            detailsquery = "SELECT Product_details from Products WHERE Product_name = %s"
            cursor.execute(detailsquery, (product_name,))
            details = cursor.fetchone()[0]

            # Fetch the product image
            picquery = "SELECT Product_image from Products WHERE Product_name = %s"
            cursor.execute(picquery, (product_name,))
            image_data = cursor.fetchone()[0]

            pixmap = QPixmap()
            pixmap.loadFromData(image_data)

            # Set the values on the UI elements
            self.DeName.setText(product_name)
            self.DeImage.setPixmap(pixmap)
            self.DeDetails.setText(details)
            self.DePrice.setText(str(MinPrice))


            #Specs
            storagecomboque= "SELECT DISTINCT(Storage) FROM specificproducts WHERE Product_name = %s"
            cursor.execute(storagecomboque, (product_name,))
            storage = cursor.fetchall()

            for item in storage:
                self.DstorageBox.addItem(item[0])
            ramcomboque= "SELECT DISTINCT(RAM) FROM specificproducts WHERE Product_name = %s"
            cursor.execute(ramcomboque, (product_name,))
            rams = cursor.fetchall()

            for item in rams:
                self.DramBox.addItem(item[0])
            self.DramBox.currentIndexChanged.connect(self.SpecificProduct)
            self.DstorageBox.currentIndexChanged.connect(self.SpecificProduct)
            
            #Available
            ram = self.DramBox.currentText()
            storage = self.DstorageBox.currentText()
            if ram and storage:
                self.Stockcheck()

        proquery = "SELECT Product_name FROM products"
        cursor.execute(proquery)
        self.labels = [row[0] for row in cursor.fetchall()]
    
    def SpecificProduct(self):
        product_name = self.DeName.text()
        ram = self.DramBox.currentText()
        storage = self.DstorageBox.currentText()
        branch = self.Bline.text()
        if ram and storage:
            query = "SELECT Spec_ID FROM specificproducts WHERE Product_name = %s AND Ram = %s AND Storage = %s"
            cursor.execute(query, (product_name, ram, storage))
            result = cursor.fetchone()
            if result:
                ID = result[0]
                Ppricequery = "SELECT Price FROM specificproducts WHERE Spec_ID = %s"
                cursor.execute(Ppricequery, (ID,))
                Price = cursor.fetchone()[0]
                if Price:
                    price = str(Price)
                    self.DePrice.setText(f"Gh¢{price}")

                    invquery = f"SELECT {branch} FROM inventory WHERE Spec_ID = %s"
                    cursor.execute(invquery, (ID,))
                    invresult = cursor.fetchone()
                    if invresult:
                        self.InStore.setText(f"Available: {invresult[0]}")
            else:
                    self.DePrice.setText("Spec not available")
                    self.InStore.setText("")
        else:
            self.DePrice.setText("Spec not available")
            self.InStore.setText("")
            
    def Stockcheck(self):
        qty = self.Qty.text()
        product_name = self.DeName.text()
        ram = self.DramBox.currentText()
        storage = self.DstorageBox.currentText()
        #if ram and storage:
        query = "SELECT Spec_ID FROM specificproducts WHERE Product_name = %s AND Ram = %s AND Storage = %s"
        cursor.execute(query, (product_name, ram, storage))
        result = cursor.fetchone()
        if result:
            branch = f"{self.Bline.text()}"
            ID = result[0]
            InStoreQ = f"SELECT {branch} FROM inventory WHERE Spec_ID = %s"
            cursor.execute(InStoreQ, (ID,))
            instore = cursor.fetchone()[0]
            if int(instore) < int(qty):
                query = "SELECT Branch_name FROM branch"
                cursor.execute(query)
                branches = cursor.fetchall()
                store =[]
                stqty = []
                disp = ""
                for branch in branches:
                    brname = f"{branch[0]}"
                    query = f"SELECT {brname} FROM inventory WHERE Spec_ID = %s"
                    cursor.execute(query, (ID,))
                    data = cursor.fetchone()
                    if data and int(data[0]) > int(qty):
                        store.append(brname)
                        stqty.append(data[0])
                disp += "Quantity exceeds stock!\nAlternative stores:\n"
                for brname, qty_available in zip(store, stqty):
                    disp += f"{brname} : {qty_available} pcs available\n"

                if self.View.text() != disp: #self.View.text()=="" or    
                    self.View.setText(disp)
            elif self.Qty == 0:
                query = "SELECT Branch_name FROM branch"
                cursor.execute(query)
                branches = cursor.fetchall()
                store =[]
                stqty = []
                disp = ""
                for branch in branches:
                    brname = f"{branch[0]}"
                    query = f"SELECT {brname} FROM inventory WHERE Spec_ID = %s"
                    cursor.execute(query, (ID,))
                    data = cursor.fetchone()
                    if data and int(data[0]) > 0:
                        store.append(brname)
                        stqty.append(data[0])
                disp += "Quantity exceeds stock!\nAlternative stores:\n"
                for brname, qty_available in zip(store, stqty):
                    disp += f"{brname} : {qty_available} pcs available\n"
            else:
                self.View.clear()
        #self.AddtoCartButton.clicked.connect(self.AddtoCart)   
    
    def qtydec(self):
        Qty = self.Qty.text()
        if int(Qty) > 1:
            Qty = int(Qty)-1
            self.Qty.setText(str(Qty))
    def qtyinc(self):
        Qty = self.Qty.text()
        Qty = int(Qty)+1
        self.Qty.setText(str(Qty))

    def Products(self):
        self.CartTable.hide()
        self.CheckoutWid.hide()
        self.ProFrame.show()
        self.ProDetails.show()

    def Cart(self):
        self.CartTable.show()
        self.CheckoutWid.show()
        self.ProDetails.hide()
        self.ProFrame.hide()
        self.ClearCart.clicked.connect(self.ClearC)
        self.ClearP()


    def AddtoCart(self):
    # Create a remove button
        remove_button = QToolButton()
        remove_button.setText("Remove")
        remove_button.setToolTip("Click to remove")
        remove_button.setStyleSheet('border:none')
        remove_button.setCursor(Qt.PointingHandCursor)
        
        # Create a widget to hold the remove button
        button_widget = QWidget()
        button_layout = QHBoxLayout()
        button_layout.addWidget(remove_button)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_widget.setLayout(button_layout)

        # Retrieve product details
        qty = self.Qty.text()
        product_name = self.DeName.text()
        ram = self.DramBox.currentText()
        storage = self.DstorageBox.currentText()
        price_per_unit = self.DePrice.text()

        if not (ram and storage and qty):
            QMessageBox.warning(self, "Input Error", "Please fill in all fields.")
            return

        try:
            # Retrieve product ID from the database
            query = "SELECT Spec_ID FROM specificproducts WHERE Product_name = %s AND Ram = %s AND Storage = %s"
            cursor.execute(query, (product_name, ram, storage))
            result = cursor.fetchone()

            if result:
                product_id = result[0]
            else:
                QMessageBox.warning(self, "Product Error", "Product not found.")
                return

            # Check if the product already exists in the cart
            row_count = self.CartTable.rowCount()
            product_exists = False

            for row in range(row_count):
                item_id = self.CartTable.item(row, 0)
                if item_id and item_id.text() == str(product_id):
                    qty_item = self.CartTable.item(row, 2)
                    if qty_item:
                        current_qty = int(qty_item.text())
                        new_qty = current_qty + int(qty)
                        self.CartTable.setItem(row, 2, QtWidgets.QTableWidgetItem(str(new_qty)))
                        product_exists = True
                        break

            if not product_exists:
                # Add the new product to the cart table
                row_position = self.CartTable.rowCount()
                self.CartTable.insertRow(row_position)
                self.CartTable.setItem(row_position, 0, QtWidgets.QTableWidgetItem(str(product_id)))
                self.CartTable.setItem(row_position, 1, QtWidgets.QTableWidgetItem(product_name))
                self.CartTable.setItem(row_position, 2, QtWidgets.QTableWidgetItem(qty))
                self.CartTable.setItem(row_position, 3, QtWidgets.QTableWidgetItem(price_per_unit))
                self.CartTable.setCellWidget(row_position, 4, button_widget)

            # Generate and set the order ID    
            now = self.Chdatime.dateTime()
            order_id = now.toString("yyMMddHHmmsszzz")
            #self.EmpName.setText(person)
            #self.BrName.setText(branch)
            self.OrdID.setText(order_id)
            self.update()

            # Connect the remove button to the remove_row method
            remove_button.clicked.connect(self.remove_row)

            # Clear the view if necessary
            self.View.setText("")
                
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred: {str(e)}")

    def AddtoCart0(self):
    # Create a remove button
        remove_button = QToolButton()
        remove_button.setText("Remove")
        remove_button.setToolTip("Click to remove")
        remove_button.setStyleSheet('border:none')
        remove_button.setCursor(Qt.PointingHandCursor)
        
        # Create a widget to hold the remove button
        button_widget = QWidget()
        button_layout = QHBoxLayout()
        button_layout.addWidget(remove_button)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_widget.setLayout(button_layout)

        qty = self.Qty.text()
        product_name = self.DeName.text()
        ram = self.DramBox.currentText()
        storage = self.DstorageBox.currentText()
        perpc = self.DePrice.text()

        if ram and storage:
            exists = False
            rows = self.CartTable.rowCount()
            query = "SELECT Spec_ID FROM specificproducts WHERE Product_name = %s AND Ram = %s AND Storage = %s"
            cursor.execute(query, (product_name, ram, storage))
            result = cursor.fetchone()
            ID = result[0]

            for row in range(rows):
                pid = self.CartTable.item(row, 0)
                if pid and pid.text() == str(ID): 
                    qty_item = self.CartTable.item(row, 2)
                    if qty_item:
                        current_qty = int(qty_item.text())
                        new_qty = current_qty + int(qty)
                        self.CartTable.setItem(row, 2, QtWidgets.QTableWidgetItem(str(new_qty)))
                        exists = True
                        break

            if not exists:
                # Add the new product to the cart table
                row_position = self.CartTable.rowCount()
                self.CartTable.insertRow(row_position)
                self.CartTable.setItem(row_position, 0, QtWidgets.QTableWidgetItem(str(ID)))
                self.CartTable.setItem(row_position, 1, QtWidgets.QTableWidgetItem(product_name))
                self.CartTable.setItem(row_position, 2, QtWidgets.QTableWidgetItem(qty))
                self.CartTable.setItem(row_position, 3, QtWidgets.QTableWidgetItem(perpc))
                self.CartTable.setCellWidget(row_position, 4, button_widget)

                # Generate and set the order ID    
                now = self.Chdatime.dateTime()
                order_id = now.toString("yyMMddHHmmsszzz")
                #self.EmpName.setText(person)
                #self.BrName.setText(branch)
                self.OrdID.setText(order_id)
                self.update()

                # Connect the remove button to the remove_row method
                remove_button.clicked.connect(self.remove_row)

                # Clear the view if necessary
                self.View.setText("")
    
                
        #Update Checkout
    def update(self):
        TAmt = 0.0
        TUnits = 0
        for row in range(self.CartTable.rowCount()):
            ID = self.CartTable.item(row, 0)
            item = self.CartTable.item(row, 1)
            units = self.CartTable.item(row, 2)
            price = self.CartTable.item(row, 3).text().replace("GH¢","")
            
        Total = 0
        self.receipt.setRowCount(0)
        for row in range(self.CartTable.rowCount()):
            self.receipt.insertRow(row) 
            ID = self.CartTable.item(row, 0).text()
            item = self.CartTable.item(row, 1).text()
            units = self.CartTable.item(row, 2).text()
            price = self.CartTable.item(row, 3).text()
            self.receipt.setItem(row, 0, QTableWidgetItem(ID))
            self.receipt.setItem(row, 1, QTableWidgetItem(item))
            self.receipt.setItem(row, 2, QTableWidgetItem(units))
            self.receipt.setItem(row, 3, QTableWidgetItem(price))
            
            #Receipt Calcs
            pricequery = "SELECT Price FROM specificproducts WHERE Spec_ID = %s"
            cursor.execute(pricequery, (ID,))
            result = cursor.fetchone()[0]
            Qprice = str(result)
            Total += int(units) * float(Qprice)

        self.TAmount.setText(str(Total))


    def remove_row(self):
        button  = self.sender()
        for row in range(self.CartTable.rowCount()):
            widget = self.CartTable.cellWidget(row, 4)
            if widget:
                remove_button = widget.layout().itemAt(0).widget()
                if remove_button == button:
                    self.CartTable.removeRow(row)
        self.update()

    def ClearC(self):
        self.CartTable.setRowCount(0) 
        self.TAmount.setText(None)
        self.OrdID.setText(None)
        self.receipt.setRowCount(0)
    def ClearP(self):
        self.DeImage.clear()
        self.InStore.clear()
        self.DeDetails.clear()
        self.DeName.clear()
        self.DePrice.clear()
        self.View.clear()
        self.Qty.clear()
        self.DramBox.clear()
        self.DstorageBox.clear()
    def ConOrder(self):
        order_id = self.OrdID.text()
        date = QDate.currentDate()
        or_date = date.toString('yyyy-MM-dd')
        branch = self.Bline.text()
        for row in range(self.CartTable.rowCount()):
            itemID = self.CartTable.item(row, 0).text()
            units = self.CartTable.item(row, 2).text()
            Units = int(units)
            #sale update
            query = "INSERT INTO sales (Order_ID, Branch_name, Spec_ID, Quantity, Sale_Date) values (%s,%s, %s, %s, %s)"
            values = (order_id, branch, itemID, Units, or_date)
            cursor.execute(query, values)
            db.commit()
            #Inv update
            uquery = f"UPDATE inventory SET {branch} = ({branch} - %s) WHERE Spec_ID = %s"
            cursor.execute(uquery, (Units, itemID))
            db.commit()
        self.getReceipt()
        self.ClearC()
        self.ClearP()
    def logout(self):
        Confirm = QMessageBox.information(None, "Warning", "Are you sure you want to logout and exit", QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)
        if Confirm == QMessageBox.Ok:
            sys.exit()
#     

    def getReceipt(self):
        orderid = f"Order ID: {self.OrdID.text()}"
        date = f"{self.Chdatime.dateTime().toString()}"
        label7 = "Cart Summary"
        
        receipt = self.receipt  
        row_count = receipt.rowCount()
        column_count = receipt.columnCount()
        
        # Open a file dialog to choose where to save the file
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save As", f"{self.OrdID.text()}.pdf", "PDF Files (*.pdf);;All Files (*)", options=options)
        
        if file_name:
            # Set up the PDF writer
            person = self.Uline.text()
            branch = self.Bline.text()
            total = self.TAmount.text()
            pdf_writer = QPdfWriter(file_name)
            pdf_writer.setPageSize(QPdfWriter.A6)
            pdf_writer.setResolution(300)
            
            painter = QPainter(pdf_writer)
            
            # Set up the font
            font = QFont('Arial', 10)
            painter.setFont(font)
            
            # Get page size
            page_rect = painter.viewport()  # Get the page size from the painter's viewport
            page_width = page_rect.width()
            
            # Draw the header
            y_position = 100
            
            painter.drawText(QPointF(10, y_position), orderid)
            y_position += 90
            painter.drawText(QPointF(10, y_position), date)
            y_position += 90
            painter.drawText(QPointF(10, y_position), label7)
            y_position += 110  # Space before table
            
            # Draw table headers
            painter.drawText(QPointF(90, y_position), "Items")
            painter.drawText(QPointF(600, y_position), "Quantity")
            painter.drawText(QPointF(900, y_position), "Unit Price")
            y_position += 70
            
            # Draw table content
            for row in range(row_count):
                row_data = []
                for column in range(column_count):
                    item = receipt.item(row, column)
                    if item is not None:
                        row_data.append(item.text())
                    else:
                        row_data.append("")  # Handle empty cells
                    
                # Format and draw each row
                row_text = f"{row_data[0]:<5}{row_data[1]:<30}{row_data[2]:<15}{row_data[3]:<45}"
                painter.drawText(QPointF(10, y_position), row_text)
                y_position += 70

            painter.drawText(QPointF(20, 600), f"Served By: {person}")
            painter.drawText(QPointF(20, 650), f"Branch : {branch}")
            painter.drawText(QPointF(20, 700), f"Amount Paid: {total}")
            y_position += 70
            painter.end()

#def main
import ctypes
def screendim():
    user32 = ctypes.windll.user32
    width = user32.GetSystemMetrics(0)
    height = user32.GetSystemMetrics(1)
    return width, height
width, height = screendim()

#def main
def main():
    app = QApplication(sys.argv)
    welcome = EmpDboard()
    widget = QStackedWidget()
    widget.addWidget(welcome) 
    widget.setWindowTitle("My logistics App")
    widget.resize(int(width), int(height))
    widget.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()

'''app = QApplication(sys.argv)

welcome = EmpDboard()
widget = QStackedWidget()
widget.addWidget(welcome) 
widget.setWindowTitle("My logistics App")
widget.resize(int(width), int(height))
widget.show()
sys.exit(app.exec())'''