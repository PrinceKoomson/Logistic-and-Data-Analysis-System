import sys
import os
import secrets
import string
import re
import hashlib
import string
import secrets

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PyQt5 import QtWidgets, QtGui
from PyQt5.uic import loadUi
from PyQt5.QtCore import QDate, Qt, QDateTime, QTimer, QRect, QSize, QPropertyAnimation
from PyQt5.QtWidgets import (
    QApplication, QDialog, QStackedWidget, QMessageBox, QTableWidgetItem, QAbstractItemView,
    QFileDialog, QLineEdit, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QButtonGroup, QListView, QStyledItemDelegate, QWidget, QToolButton, QPushButton, QSizePolicy, QListWidgetItem, QTableWidget, QListWidget
)
from PyQt5.QtGui import (
    QDoubleValidator, QIntValidator, QColor, QFont, QFontMetrics, QPainter,
    QStandardItem, QStandardItemModel, QPixmap, QBrush
)  
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


from  Manager import ManReporting

#database connection
import mysql.connector as con
db = con.connect(host="127.0.0.1", user="root", password ="", database ="logisticsdb")
cursor = db.cursor()


class ADboard(QDialog):
    def __init__(self):
        super(ADboard, self).__init__()
        main_dir = os.path.dirname(os.path.abspath(__file__))
        Ui = os.path.join(main_dir, 'Ui', 'Admin2.ui')
        loadUi(Ui, self)
        self.senderName = "Admin"
        #self.MessageArea.hide()
        self.BranchTable.hide()
        self.EmployeeTable.hide()
        self.InventoryTable.hide()
        self.ProductTable.hide()
        self.ReportTable.hide()
        #Header
        header = self.Header
        hlayout = QHBoxLayout()
        hlayout.addWidget(self.Hlabel, alignment=Qt.AlignCenter)
        self.Hlabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        header.setLayout(hlayout)
        hstyle=('''
            QWidget {
                background-color: #2c3e50;
                color: white;
                border: none;
            }
            
            QLabel {
                font-family: 'Palatino Linotype';
                color: #00ff00;
                font-size: 55px;
                font-weight: bold;
                padding: 10px;
            }
        ''')
        header.setStyleSheet(hstyle)
        #footer
        self.footer.setStyleSheet(hstyle)

        #Main Menu
        menustyle = '''
            QListWidget {
                background-color: #2c3e50;  /* Dark blue-gray background */
                color: white;
                border: none;
                outline: none;
            }

            QListWidget::item {
                padding: 5px 5px;
                font-size: 16px;
                color: white;
            }

            QListWidget::item:hover {
                background-color: #34495e;  /* Slightly lighter blue-gray on hover */
            }

            QListWidget::item:focus {
                outline: none;  /* Remove dotted lines when focused */
                border: none;
            }'''
        self.MenuList.setStyleSheet(menustyle)
        #self.MenuList.setSelectionMode(QListWidget.NoSelection)
        self.ButtonList.setStyleSheet(menustyle)
     
        buttons = ["Inventory", "Stores", "Employees", "Products", "Report", "LogOut"]
        for btn_name in buttons:
            btn = QToolButton()
            #btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            btn.setText(btn_name)
            btn.setObjectName(f"{btn_name}btn")
            btn.setStyleSheet("background-color: lightgray; border:none;")

            btnW = QWidget()
            btnlay = QHBoxLayout()

            btnlay.addWidget(btn)
            btnW.setLayout(btnlay)

            item = QListWidgetItem()
            item.setSizeHint(QSize(150, 90))
            self.MenuList.addItem(item)
            self.MenuList.setItemWidget(item, btnW)
            btn.clicked.connect(getattr(self, btn_name))
        toolbcss = '''
            QToolButton {
                background-color: #2c3e50;  /* Blue background */
                color: white;
                padding: 0px 0px;
                margin: 0px 0px 0px 0px;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                height = 20px;
                width = 50px;
            }

            QToolButton:hover {
                background-color: #0066cc;  /* Darker blue on hover */
            }

            QToolButton:focus {
                outline: none;
                border: 2px solid #007bff;  /* Blue outline when focused */
            }

            QToolButton:pressed {
                background-color: #0055aa;  /* Darker blue when pressed */
            }
            '''
        button_names = ["Inventorybtn", "Storesbtn", "Employeesbtn", "Productsbtn", "Reportbtn", "LogOutbtn"]
        for name in button_names:
            btn = self.findChild(QToolButton, name)
            if btn:
                btn.setStyleSheet(toolbcss)
                btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)#QSize(150, 40))
        self.homewid.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.homewid.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        # Apply hover effect after the widget is fully shown
        self.init_hover_effects()
        self.refreshInv()
        self.homepage()
        self.MessageButton.clicked.connect(self.Messages)
    def homepage(self):
        query = "SELECT DATE(Sale_Date) AS day, SUM(Quantity) AS total_quantity FROM sales GROUP BY DATE(Sale_Date) ORDER BY DATE(Sale_Date)"
        cursor.execute(query)
        result = cursor.fetchall()
        sales_data = pd.DataFrame(result, columns=['date', 'sales'])
       
        self.reporting = ManReporting()
 
        # SoldBox
        self.sold_label = QLabel("Sold:")
        self.count_label = QLabel("675")
        self.sold_label.setAlignment(Qt.AlignCenter)
        self.count_label.setAlignment(Qt.AlignCenter)
        self.sold_label.setStyleSheet("color: green; font-size: 24px; font-weight: bold;")
        self.count_label.setStyleSheet("color: green; font-size: 48px; font-weight: bold;")
    
        layout = QVBoxLayout()
        layout.addWidget(self.sold_label)
        layout.addWidget(self.count_label)
        
        sheet =("""
            QWidget {
                background-color: white;
            }
            QLabel {
                margin: 10px;
            }
        """)
        SoldBox = QWidget()
        SoldBox.setLayout(layout)
        SoldBox.setStyleSheet(sheet)

        # Goods Box
        self.stock = QLabel("In Stock")
        self.stock.setStyleSheet("color: green; font-size: 24px; font-weight: bold;")
        self.stockCount = QLabel("950")
        self.stockCount.setStyleSheet("color: green; font-size: 48px; font-weight: bold;")
        self.stock.setAlignment(Qt.AlignCenter)
        self.stockCount.setAlignment(Qt.AlignCenter)
        
        slayout = QVBoxLayout()
        slayout.addWidget(self.stock)
        slayout.addWidget(self.stockCount)
        StockBox = QWidget()
        
        slayout.setAlignment(Qt.AlignCenter)
        StockBox.setFixedWidth(150)
        StockBox.setLayout(slayout)
        StockBox.setStyleSheet(sheet)

        canvas = self.reporting.line_chart(sales_data, "date", "sales", title=None, x_label=None, y_label=None)
        GraphBox = QWidget()
        Gralayout = QVBoxLayout()
        Gralayout.addWidget(canvas)
        GraphBox.setLayout(Gralayout)
        GraphBox.setFixedWidth(350)

        Hbox = QHBoxLayout()
        Hbox.addWidget(SoldBox)
        Hbox.addWidget(StockBox)
        Hbox.addWidget(GraphBox)
        Hbox.setContentsMargins(110, 0, 110, 0)
        
        Ovrview = QWidget()
        Ovrview.setFixedHeight(150)
        Ovrview.setLayout(Hbox)

        Hbox_item = QListWidgetItem()
        #Hbox_item.setSizeHint(QSize(Hbox.sizeHint()))
        Hbox_item.setSizeHint(QSize(100, 150))
        self.homewid.addItem(Hbox_item)
        self.homewid.setItemWidget(Hbox_item, Ovrview)


        table = self.duplicate_table(self.InventoryTable)
        table.insertColumn(0)
        table.setHorizontalHeaderItem(0, QTableWidgetItem(""))
        prods = self.refreshInv()
        for p, pdata in enumerate(prods):
            pro = QTableWidgetItem(pdata)
            table.setItem(p, 0, pro)


        table.verticalHeader().setVisible(False)
        table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        table.verticalHeader().setVisible(False)
        #table.setStyleSheet("border-left: 1px solid")
        table.setColumnWidth(0, 300)
        table.setColumnWidth(1, 125)
        table.setColumnWidth(2, 125)
        table.setColumnWidth(3, 125)
        table.setColumnWidth(4, 125)

        layout = QHBoxLayout()
        layout.addWidget(table)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(50, 50, 50, 50)
        tab = QWidget()
        tab.setLayout(layout)
        #hei = self.adjust_table_height(self.InventoryTable.height())

        titem = QListWidgetItem()
        titem.setSizeHint(QSize(00, 600))
        

        self.homewid.addItem(titem)
        self.homewid.setItemWidget(titem, tab)
        btncss = '''
            QToolButton {
                background-color: #2c3e50;  /* Blue background */
                color: white;
                padding: 0px 0px;
                margin: 0px 0px 0px 0px;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                height = 20px;
                width = 50px;
            }

            QToolButton:hover {
                background-color: #0066cc;  /* Darker blue on hover */
            }

            QToolButton:focus {
                outline: none;
                border: 2px solid #007bff;  /* Blue outline when focused */
            }

            QToolButton:pressed {
                background-color: #0055aa;  /* Darker blue when pressed */
            }
            '''
        buttons = ["Add_Inventory", "Distribute"]#, "Manage"]
        for btn_name in buttons:
            btn = QToolButton()
            btn.setText(btn_name)
            btn.setObjectName(f"{btn_name}btn")
            btn.setStyleSheet(btncss)
            btnW = QWidget()
            btnlay = QHBoxLayout()
            btnlay.addWidget(btn)
            btnW.setLayout(btnlay)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

            item = QListWidgetItem()
            item.setSizeHint(QSize(150, 90))
            self.ButtonList.addItem(item)
            self.ButtonList.setItemWidget(item, btnW)
            # Connect button to the corresponding method
            btn.clicked.connect(getattr(self, btn_name))

    def Inventory(self):
        #self.MessageArea.hide()
        self.homewid.clear()
        self.ButtonList.clear()
        self.refreshInv()
        self.homepage()

        menustyle_selected = '''
                QWidget {
                    background-color: #1abc9c;  /* Teal color for selected item */
                    color: white;
                }

                QToolButton {
                    color: white;
                }
            '''
        for i in range(self.MenuList.count()):
            widget_item = self.MenuList.itemWidget(self.MenuList.item(i))
            btn = widget_item.findChild(QToolButton)
            if btn and btn.text() == "Inventory":
                widget_item.setStyleSheet(menustyle_selected)
            else:
                widget_item.setStyleSheet("")

    def adjust_table_height(self, table):
        # Resize rows to fit their contents
        table.resizeRowsToContents()

        # Calculate the total height needed for all rows
        total_height = table.horizontalHeader().height()  # Header height

        for row in range(table.rowCount()):
            total_height += table.rowHeight(row)  # Sum of all row heights

        # Add extra space for the horizontal scrollbar if needed
        if table.horizontalScrollBar().isVisible():
            total_height += table.horizontalScrollBar().height()

        return total_height
    def refreshInv(self):
        self.InventoryTable.setRowCount(0)
        self.InventoryTable.setColumnCount(0)

        spquery = "SELECT specificproducts.Spec_ID, specificproducts.Product_name FROM specificproducts"

        cursor.execute(spquery)
        prods = cursor.fetchall()
        products = []
        for row, (spec_id, product_name) in enumerate(prods):
            self.InventoryTable.insertRow(row)
            pro = f"{spec_id}-{product_name}"
            products.append(pro)

        brquery = "SELECT Branch_name FROM branch"
        cursor.execute(brquery)
        stores = cursor.fetchall()
        for col, (colh,) in enumerate(stores):
            self.InventoryTable.insertColumn(col)
            self.InventoryTable.setHorizontalHeaderItem(col, QTableWidgetItem(colh))
        self.InventoryTable.insertColumn(col+1)
        self.InventoryTable.insertColumn(col+2)
        self.InventoryTable.setHorizontalHeaderItem(col+1, QTableWidgetItem("In stock"))
        self.InventoryTable.setHorizontalHeaderItem(col+2, QTableWidgetItem("Total"))
        #To populate
        query = "SELECT `Computech`, `FlexConsult`, `In_stock`, Total FROM inventory"
        cursor.execute(query)
        dist = cursor.fetchall()

        for row, row_data in enumerate(dist):
            for col, data in enumerate(row_data):
                item = QTableWidgetItem(str(data))
                self.InventoryTable.setItem(row, col, item)
        self.InventoryTable.setSizeAdjustPolicy(QTableWidget.AdjustToContents)
        #self.adjust_table_height(self.InventoryTable)

        return products

        #Inv(self)
    def Add_Inventory(self):
        form = AddInv()
        form.exec()
        self.refreshInv()
    def Distribute(self):
        form = ManInv()
        form.exec()
        self.refreshInv()
    
    def Stores(self):
        self.ButtonList.clear()
        self.homewid.clear()
        self.BrRefresh()
        menustyle_selected = '''
                QWidget {
                    background-color: #1abc9c;  /* Teal color for selected item */
                    color: white;
                }

                QToolButton {
                    color: white;
                }
            '''       
        for i in range(self.MenuList.count()):
            widget_item = self.MenuList.itemWidget(self.MenuList.item(i))
            btn = widget_item.findChild(QToolButton)
            if btn and btn.text() == "Stores":
                widget_item.setStyleSheet(menustyle_selected)
            else:
                widget_item.setStyleSheet("")
        #Table
        table = self.duplicate_table(self.BranchTable)
        table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        table.verticalHeader().setVisible(False)
        #table.setStyleSheet("border-left: 1px solid")
        #table.setColumnWidth(0, 450)
        layout = QHBoxLayout()
        layout.addWidget(table)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(50, 50, 50, 50)
        tab = QWidget()
        tab.setLayout(layout)
        hei = self.InventoryTable.height()

        titem = QListWidgetItem()
        titem.setSizeHint(QSize(100, hei))

        self.homewid.addItem(titem)
        self.homewid.setItemWidget(titem, tab)
        btncss = '''
            QToolButton {
                background-color: #2c3e50;  /* Blue background */
                color: white;
                padding: 0px 0px;
                margin: 0px 0px 0px 0px;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                height = 20px;
                width = 50px;
            }

            QToolButton:hover {
                background-color: #0066cc;  /* Darker blue on hover */
            }

            QToolButton:focus {
                outline: none;
                border: 2px solid #007bff;  /* Blue outline when focused */
            }

            QToolButton:pressed {
                background-color: #0055aa;  /* Darker blue when pressed */
            }
            '''
        buttons = ["Add_Store", "Edit_Store", "Delete_Store"]
        for btn_name in buttons:
            btn = QToolButton()
            btn.setText(btn_name)
            btn.setObjectName(f"{btn_name}btn")
            btn.setStyleSheet(btncss)
            btnW = QWidget()
            btnlay = QHBoxLayout()
            btnlay.addWidget(btn)
            btnW.setLayout(btnlay)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

            item = QListWidgetItem()
            item.setSizeHint(QSize(150, 90))
            self.ButtonList.addItem(item)
            self.ButtonList.setItemWidget(item, btnW)
            # Connect button to the corresponding method
            btn.clicked.connect(getattr(self, btn_name))   
    def Add_Store(self):
        form = AddStore()
        form.exec()
        self.BrRefresh()
    def Delete_Store(self):
        form = DelStore(self)
        form.exec()
        self.BrRefresh()
    def Edit_Store(self):
        a=0
    def BrRefresh(self):
        self.BranchTable.setColumnWidth(0, 120)
        self.BranchTable.setColumnWidth(1, 235)
        self.BranchTable.setColumnWidth(2, 230)
        self.BranchTable.setColumnWidth(3, 235)
        query = "SELECT Branch_ID, Branch_name, Branch_location, Branch_Manager FROM branch"
        cursor.execute(query)
        result = cursor.fetchall()
        self.BranchTable.setRowCount(0)
        for row_num, row_data in enumerate(result):
            self.BranchTable.insertRow(row_num)
            for col_num, data in enumerate(row_data):
                self.BranchTable.setItem(row_num, col_num, QTableWidgetItem(str(data)))

    def Employees(self):
        self.ButtonList.clear()
        self.homewid.clear()
        self.EmRefresh()
        menustyle_selected = '''
                QWidget {
                    background-color: #1abc9c;  /* Teal color for selected item */
                    color: white;
                }

                QToolButton {
                    color: white;
                }
            '''       
        for i in range(self.MenuList.count()):
            widget_item = self.MenuList.itemWidget(self.MenuList.item(i))
            btn = widget_item.findChild(QToolButton)
            if btn and btn.text() == "Employees":
                widget_item.setStyleSheet(menustyle_selected)
            else:
                widget_item.setStyleSheet("")
        #table
        table = self.duplicate_table(self.EmployeeTable)
        table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        table.verticalHeader().setVisible(False)
        #table.setStyleSheet("border-left: 1px solid")
        #table.setColumnWidth(0, 450)
        layout = QHBoxLayout()
        layout.addWidget(table)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(50, 50, 50, 50)
        tab = QWidget()
        tab.setLayout(layout)
        hei = self.InventoryTable.height()

        titem = QListWidgetItem()
        titem.setSizeHint(QSize(100, hei))

        self.homewid.addItem(titem)
        self.homewid.setItemWidget(titem, tab)
        btncss = '''
            QToolButton {
                background-color: #2c3e50;  /* Blue background */
                color: white;
                padding: 0px 0px;
                margin: 0px 0px 0px 0px;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                height = 20px;
                width = 50px;
            }

            QToolButton:hover {
                background-color: #0066cc;  /* Darker blue on hover */
            }

            QToolButton:focus {
                outline: none;
                border: 2px solid #007bff;  /* Blue outline when focused */
            }

            QToolButton:pressed {
                background-color: #0055aa;  /* Darker blue when pressed */
            }
            '''
        buttons = ["Add_Employee", "Edit_Employee", "Delete_Employee"]
        for btn_name in buttons:
            btn = QToolButton()
            btn.setText(btn_name)
            btn.setObjectName(f"{btn_name}btn")
            btn.setStyleSheet(btncss)
            btnW = QWidget()
            btnlay = QHBoxLayout()
            btnlay.addWidget(btn)
            btnW.setLayout(btnlay)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

            item = QListWidgetItem()
            item.setSizeHint(QSize(150, 90))
            self.ButtonList.addItem(item)
            self.ButtonList.setItemWidget(item, btnW)
            # Connect button to the corresponding method
            btn.clicked.connect(getattr(self, btn_name))
    def Add_Employee(self):
        form = AddEmployee(self)
        form.exec()
        self.EmRefresh()
    def Delete_Employee(self):
        form = DelEmployee(self)
        form.exec()
        self.EmRefresh()
    def Edit_Employee(self):
        form = EditEmployee(self)
        form.exec()
        self.EmRefresh
    def EmRefresh(self):
        self.EmployeeTable.setColumnWidth(0, 100)
        self.EmployeeTable.setColumnWidth(1, 250)
        self.EmployeeTable.setColumnWidth(2, 160)
        self.EmployeeTable.setColumnWidth(3, 160)
        self.EmployeeTable.setColumnWidth(4, 150)
        
        query = "SELECT ID, CONCAT(First_name, ' ', Last_name) AS FullName, Phone, Position,  Branch_name FROM managers UNION SELECT ID, CONCAT(First_name, ' ', Last_name) AS FullName, Phone, Position,  Branch_name FROM salespersons ORDER BY FullName"
        cursor.execute(query)
        result = cursor.fetchall()
        self.EmployeeTable.setRowCount(0)
        for row_num, row_data in enumerate(result):
            self.EmployeeTable.insertRow(row_num)
            for col_num, data in enumerate(row_data):
                self.EmployeeTable.setItem(row_num, col_num, QTableWidgetItem(str(data)))

    def Products(self):
        self.ButtonList.clear()
        self.homewid.clear()
        self.PrRefresh()
        menustyle_selected = '''
                QWidget {
                    background-color: #1abc9c;  /* Teal color for selected item */
                    color: white;
                }

                QToolButton {
                    color: white;
                }
            '''       
        for i in range(self.MenuList.count()):
            widget_item = self.MenuList.itemWidget(self.MenuList.item(i))
            btn = widget_item.findChild(QToolButton)
            if btn and btn.text() == "Products":
                widget_item.setStyleSheet(menustyle_selected)
            else:
                widget_item.setStyleSheet("")

        #Table
        table = self.duplicate_table(self.ProductTable)
        table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        table.verticalHeader().setVisible(False)
        #table.setStyleSheet("border-left: 1px solid")
        #table.setColumnWidth(0, 450)
        layout = QHBoxLayout()
        layout.addWidget(table)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(50, 50, 50, 50)
        tab = QWidget()
        tab.setLayout(layout)
        hei = self.InventoryTable.height()

        titem = QListWidgetItem()
        titem.setSizeHint(QSize(100, hei))

        self.homewid.addItem(titem)
        self.homewid.setItemWidget(titem, tab)

        btncss = '''
            QToolButton {
                background-color: #2c3e50;  /* Blue background */
                color: white;
                padding: 0px 0px;
                margin: 0px 0px 0px 0px;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                height = 20px;
                width = 50px;
            }

            QToolButton:hover {
                background-color: #0066cc;  /* Darker blue on hover */
            }

            QToolButton:focus {
                outline: none;
                border: 2px solid #007bff;  /* Blue outline when focused */
            }

            QToolButton:pressed {
                background-color: #0055aa;  /* Darker blue when pressed */
            }
            '''
        buttons = ["Add_Product", "Delete_Product"]
        for btn_name in buttons:
            btn = QToolButton()
            btn.setText(btn_name)
            btn.setObjectName(f"{btn_name}btn")
            btn.setStyleSheet(btncss)
            btnW = QWidget()
            btnlay = QHBoxLayout()
            btnlay.addWidget(btn)
            btnW.setLayout(btnlay)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

            item = QListWidgetItem()
            item.setSizeHint(QSize(150, 90))
            self.ButtonList.addItem(item)
            self.ButtonList.setItemWidget(item, btnW)

            btn.clicked.connect(getattr(self, btn_name))
    def Add_Product(self):
        form = AddProduct(self)
        form.exec()
        self.PrRefresh()
    def Delete_Product(self):
        form = DelProduct(self)
        form.exec()
        self.PrRefresh()
    def PrRefresh(self):
        self.ProductTable.setColumnWidth(0, 150)
        self.ProductTable.setColumnWidth(1, 350)
        self.ProductTable.setColumnWidth(2, 320)
        query = "SELECT Product_ID, Product_Name FROM Products"
        cursor.execute(query)
        result = cursor.fetchall()
        
        self.ProductTable.setRowCount(0)
        for row_num, row_data in enumerate(result):
            self.ProductTable.insertRow(row_num)
            minpricequery = "SELECT MIN(Price) FROM specificproducts WHERE Product_name = %s"
            cursor.execute(minpricequery, (row_data[1],))
            MinPrice = cursor.fetchone()[0]
            maxpricequery = "SELECT MAX(Price) FROM specificproducts WHERE Product_name = %s"
            cursor.execute(maxpricequery, (row_data[1],))
            MaxPrice = cursor.fetchone()[0]
            PriceRange = f"{MinPrice} - {MaxPrice}"
            for col_num, data in enumerate(row_data):
                self.ProductTable.setItem(row_num, col_num, QTableWidgetItem(str(data)))
            self.ProductTable.setItem(row_num, 2, QTableWidgetItem(str(PriceRange)))

    def Report(self):
        self.ButtonList.clear()
        self.homewid.clear()
        self.RepAI()

        menustyle_selected = '''
                QWidget {
                    background-color: #1abc9c;  /* Teal color for selected item */
                    color: white;
                }

                QToolButton {
                    color: white;
                }
            '''       
        for i in range(self.MenuList.count()):
            widget_item = self.MenuList.itemWidget(self.MenuList.item(i))
            btn = widget_item.findChild(QToolButton)
            if btn and btn.text() == "Report":
                widget_item.setStyleSheet(menustyle_selected)
            else:
                widget_item.setStyleSheet("")
        btncss = '''
            QToolButton {
                background-color: #2c3e50;  /* Blue background */
                color: white;
                padding: 0px 0px;
                margin: 0px 0px 0px 0px;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                height = 20px;
                width = 50px;
            }

            QToolButton:hover {
                background-color: #0066cc;  /* Darker blue on hover */
            }

            QToolButton:focus {
                outline: none;
                border: 2px solid #007bff;  /* Blue outline when focused */
            }

            QToolButton:pressed {
                background-color: #0055aa;  /* Darker blue when pressed */
            }
            '''
        buttons = []
        buttonquery ="SELECT Branch_name from branch"
        cursor.execute(buttonquery)
        result = cursor.fetchall()
        if result:
            for row in result:
                branch_name = row[0]
                buttons.append(branch_name)
        branches=""
        for btn_name in buttons:
            branches = " + ".join(buttons)
            btn = QToolButton()
            btn.setText(btn_name)
            btn.setObjectName(f"{btn_name}btn")
            btn.setStyleSheet(btncss)
            btnW = QWidget()
            btnlay = QHBoxLayout()
            btnlay.addWidget(btn)
            btnW.setLayout(btnlay)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

            item = QListWidgetItem()
            item.setSizeHint(QSize(150, 90))
            self.ButtonList.addItem(item)
            self.ButtonList.setItemWidget(item, btnW)
            # Connect button to the corresponding method
            btn.clicked.connect(lambda checked, name=btn_name: self.BrReport(name))
        
        soldquery = "SELECT Product_name, sum(Quantity) AS Sold FROM sales Group by Product_name ORDER BY Product_name;"
             
        remquery = "SELECT Product_name, sum('"+branches+"') AS Remaining FROM inventory GROUP BY Product_name ORDER BY Product_name;"
        reportTable = self.RepTable(soldquery, remquery)
        #self.duplicate_table(reportTable)

        table = self.duplicate_table(reportTable)
        table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        table.verticalHeader().setVisible(False)
        layout = QHBoxLayout()
        layout.addWidget(table)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(50, 50, 50, 50)
        tab = QWidget()
        tab.setLayout(layout)
        hei = self.InventoryTable.height()
        titem = QListWidgetItem()
        titem.setSizeHint(QSize(100, hei))
        self.homewid.addItem(titem)
        self.homewid.setItemWidget(titem, tab)
    def BrReport(self, btn_name):
        self.reporting = ManReporting()
        self.detrep = Reporting()
        self.homewid.clear()
        #branch = f"{btn_name}"
        branch = btn_name
        def Ovrview():
            query = "SELECT DATE(Sale_Date) AS day, SUM(Quantity) AS total_quantity FROM sales WHERE Branch_name = %s GROUP BY DATE(Sale_Date) ORDER BY DATE(Sale_Date)"
            cursor.execute(query, (branch,))
            result = cursor.fetchall()
            sales_data = pd.DataFrame(result, columns=['date', 'sales'])
            # SoldBox
            self.sold_label = QLabel("Sold:")
            self.count_label = QLabel("675")
            self.sold_label.setAlignment(Qt.AlignCenter)
            self.count_label.setAlignment(Qt.AlignCenter)
            self.sold_label.setStyleSheet("color: green; font-size: 24px; font-weight: bold;")
            self.count_label.setStyleSheet("color: green; font-size: 48px; font-weight: bold;")
            layout0 = QVBoxLayout()
            layout0.addWidget(self.sold_label)
            layout0.addWidget(self.count_label)

            sheet =("""
                QWidget {
                    background-color: white;
                }
                QLabel {
                    margin: 10px;
                }
            """)
            SoldBox = QWidget()
            SoldBox.setLayout(layout0)
            SoldBox.setStyleSheet(sheet)
            # Stock Box
            self.stock = QLabel("In Stock")
            self.stockCount = QLabel("950")
            self.stock.setAlignment(Qt.AlignCenter)
            self.stockCount.setAlignment(Qt.AlignCenter)
            self.stock.setStyleSheet("color: green; font-size: 24px; font-weight: bold;")
            self.stockCount.setStyleSheet("color: green; font-size: 48px; font-weight: bold;")

            slayout = QVBoxLayout()
            slayout.addWidget(self.stock)
            slayout.addWidget(self.stockCount)
            StockBox = QWidget()
            
            slayout.setAlignment(Qt.AlignCenter)
            StockBox.setFixedWidth(150)
            StockBox.setLayout(slayout)
            StockBox.setStyleSheet(sheet)
            #Graph
            canvas = self.reporting.line_chart(sales_data, "date", "sales", title='', x_label='', y_label='')
            GraphBox = QWidget()
            Gralayout = QVBoxLayout()
            Gralayout.addWidget(canvas)
            GraphBox.setLayout(Gralayout)
            GraphBox.setFixedWidth(350)
            #Overview
            Hbox = QHBoxLayout()
            Hbox.addWidget(SoldBox)
            Hbox.addWidget(StockBox)
            Hbox.addWidget(GraphBox)
            Hbox.setContentsMargins(110, 0, 110, 0)
            
            Ovrview = QWidget()
            Ovrview.setFixedHeight(150)
            Ovrview.setLayout(Hbox)
            return Ovrview
        '''Hbx_item = Ovrview()
        Hbox_item = QListWidgetItem()
        Hbox_item.setSizeHint(QSize(100, 150))
        self.homewid.addItem(Hbox_item)
        self.homewid.setItemWidget(Hbox_item, Hbx_item)'''


        #Branch total Salesreport()
        #Queries for report
        saleslinequery = "SELECT DATE(Sale_Date) AS day, SUM(Quantity) AS total_quantity FROM sales WHERE Branch_name = '"+branch+"'GROUP BY DATE(Sale_Date) ORDER BY DATE(Sale_Date)"

        prbarquery = "SELECT Product_name, SUM(sales.Quantity) AS Total_Quantity FROM sales WHERE Branch_name = '"+branch+"' GROUP BY Product_name ORDER BY Product_name;"

        # Execute queries and convert results to DataFrame
        cursor.execute(saleslinequery)
        tsresult = cursor.fetchall()
        tsdf = pd.DataFrame(tsresult, columns=['date', 'sales'])

        #cursor.execute(brbarquery)
        brresult = cursor.fetchall()
        brdf = pd.DataFrame(brresult, columns=['Branch_name', 'Total_Sales'])

        cursor.execute(prbarquery)
        prresult = cursor.fetchall()
        prdf = pd.DataFrame(prresult, columns=['Product_name', 'Total_Quantity'])

        # Analyze and get graphs and summaries
        report_ai = DistributionAI(tsdf)
        TSalesgraph, sales_summary = report_ai.analyze_line_chart('date', 'sales')

        report_ai = DistributionAI(prdf)
        bargraph, product_summary = report_ai.analyze_probar_chart('Product_name', 'Total_Quantity')

        # Add graphs and summaries to self.homewid
        for graph, summary in [
            (TSalesgraph, sales_summary),
            (bargraph, product_summary)
        ]:
            widget = QWidget()
            layout = QVBoxLayout()

            canvas = FigureCanvas(graph)
            layout.addWidget(canvas)

            summary_label = QLabel(summary)
            summary_label.setWordWrap(True)
            summary_label.setAlignment(Qt.AlignCenter)
            summary_label = QLabel(summary)
            summary_label.setWordWrap(True)
            summary_label.setAlignment(Qt.AlignLeft)
            summary_label.setStyleSheet("""
                QLabel {
                    font-size: 14pt;  /* Increase font size */
                    min-height: 40px;  /* Set minimum height */
                    margin-bottom: 50px;  /* Uniform margin around the label */
                }
            """)

            layout.addWidget(summary_label)

            widget.setLayout(layout)
            widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

            list_item = QListWidgetItem(self.homewid)
            list_item.setSizeHint(widget.sizeHint())
            self.homewid.addItem(list_item)
            self.homewid.setItemWidget(list_item, widget)

        #TAble
        
        soldquery = "SELECT Product_name, sum(Quantity) AS Sold FROM sales WHERE Branch_name = '"+branch+"' Group by Product_name ORDER BY Product_name;"
        remquery = "SELECT Product_name, sum('"+branch+"') AS Remaining FROM inventory GROUP BY Product_name ORDER BY Product_name;"
        reportTable = self.RepTable(soldquery, remquery)
        #reportTable = self.RepTable((soldquery, (branch,)), (remquery, (branch,)))

        table = self.duplicate_table(reportTable)
        table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        table.verticalHeader().setVisible(False)
        layout = QHBoxLayout()
        layout.addWidget(table)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(50, 50, 50, 50)
        tab = QWidget()
        tab.setLayout(layout)
        hei = table.height()
        titem = QListWidgetItem()
        titem.setSizeHint(QSize(100, hei))
        self.homewid.addItem(titem)
        self.homewid.setItemWidget(titem, tab)

    def Salesreport(self, salesquery):
        reporting = Reporting()
        
        cursor.execute(salesquery)
        result = cursor.fetchall()
        df = pd.DataFrame(result, columns=['date', 'sales'])
        Salesgraph = reporting.line_chart(df, 'date', 'sales', title='Sales', x_label= '', y_label= '')
        container = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(Salesgraph)
        container.setLayout(layout)
        lItem = QListWidgetItem()
        lItem.setSizeHint(QSize(150,400))
        self.homewid.addItem(lItem)
        self.homewid.setItemWidget(lItem, container)
        return Salesgraph
    def BranchSalesreport(self, bquery):
        reporting = Reporting()
        cursor.execute(bquery)
        result = cursor.fetchall()
        
        df = pd.DataFrame(result, columns=['Branch_name', 'Total_Sales'])
        bargraph = reporting.bar_chart(df, x_col='Branch_name', y_col='Total_Sales', title='Total Quantity by Branch', x_label='Branch', y_label='Total_Sales')
        container = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(bargraph)
        container.setLayout(layout)

        lItem = QListWidgetItem()
        lItem.setSizeHint(QSize(150,450))
        self.homewid.addItem(lItem)
     
        self.homewid.setItemWidget(lItem, container)
        return bargraph
    def ProductSalesReport(self, psquery):
        reporting = Reporting()
        cursor.execute(psquery)
        result = cursor.fetchall()
        df = pd.DataFrame(result, columns=['Product_name', 'Total_Quantity'])

        bargraph = reporting.bar_chart(df, x_col='Product_name', y_col='Total_Quantity', title='Total Quantity by Product', x_label='Product', y_label='Total Quantity')

        container = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(bargraph)
        container.setLayout(layout)

        lItem = QListWidgetItem()
        lItem.setSizeHint(QSize(150, 450))
        self.homewid.addItem(lItem)
        self.homewid.setItemWidget(lItem, container)
        return bargraph
    
    def RepTable(self, soldquery, remquery):
        cursor.execute(soldquery)
        sold = cursor.fetchall()
        cursor.execute(remquery)
        remaining = cursor.fetchall()

        row_count = max(len(sold), len(remaining))
        self.ReportTable.setRowCount(row_count)
        for row_index, (product_name, sold_value) in enumerate(sold):
            self.ReportTable.setItem(row_index, 0, QTableWidgetItem(product_name))
            self.ReportTable.setItem(row_index, 1, QTableWidgetItem(str(sold_value)))

        for row_index, (_, remaining_value) in enumerate(remaining):
            self.ReportTable.setItem(row_index, 2, QTableWidgetItem(str(remaining_value)))
        self.ReportTable.setColumnWidth(0, 400)
        self.ReportTable.setColumnWidth(1, 200)
        self.ReportTable.setColumnWidth(2, 200)
        return self.ReportTable

    def RepAI(self):
        reporting = Reporting()
        self.homewid.clear()

        saleslinequery = "SELECT DATE(Sale_Date) AS day, SUM(Quantity) AS total_quantity FROM sales GROUP BY DATE(Sale_Date) ORDER BY DATE(Sale_Date)"
        
        brbarquery = "SELECT Branch_name, SUM(sales.Quantity * specificproducts.Price) AS Total_Sales FROM sales JOIN specificproducts ON sales.Spec_ID = specificproducts.Spec_ID GROUP BY Branch_name ORDER BY Branch_name;"
        
        prbarquery = "SELECT Product_name, SUM(sales.Quantity) AS Total_Quantity FROM sales GROUP BY Product_name ORDER BY Product_name;"

        cursor.execute(saleslinequery)
        tsresult = cursor.fetchall()
        tsdf = pd.DataFrame(tsresult, columns=['date', 'sales'])

        cursor.execute(brbarquery)
        brresult = cursor.fetchall()
        brdf = pd.DataFrame(brresult, columns=['Branch_name', 'Total_Sales'])

        cursor.execute(prbarquery)
        prresult = cursor.fetchall()
        prdf = pd.DataFrame(prresult, columns=['Product_name', 'Total_Quantity'])

        # Analyze and get graphs and recommendations
        distribution_ai = DistributionAI(tsdf)
        TSalesgraph, sales_recommendation = distribution_ai.analyze_line_chart('date', 'sales')

        distribution_ai = DistributionAI(brdf)
        Brbargraph, branch_recommendation = distribution_ai.analyze_brabar_chart('Branch_name', 'Total_Sales')

        distribution_ai = DistributionAI(prdf)
        bargraph, product_recommendation = distribution_ai.analyze_probar_chart('Product_name', 'Total_Quantity')

        # Add graphs and recommendations to self.homewid
        for graph, recommendation in [
            (TSalesgraph, sales_recommendation),
            (Brbargraph, branch_recommendation),
            (bargraph, product_recommendation)
        ]:
            widget = QWidget()
            layout = QVBoxLayout()

            # Convert matplotlib figure to canvas and add to the layout
            canvas = FigureCanvas(graph)
            layout.addWidget(canvas)

            # Add recommendation to the layout
            recommendation_label = QLabel(recommendation)
            layout.addWidget(recommendation_label)

            # Set layout to the widget
            widget.setLayout(layout)

            # Create a QListWidgetItem and set the widget as its content
            list_item = QListWidgetItem(self.homewid)
            list_item.setSizeHint(widget.sizeHint())
            self.homewid.addItem(list_item)
            self.homewid.setItemWidget(list_item, widget)

    def LogOut(self):
        Confirm = QMessageBox.information(None, "Warning", "Are you sure you want to logout and exit", QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)
        if Confirm == QMessageBox.Ok:
            sys.exit()
    
    def init_message_display(self):
        # Set item delegate for custom message display
        delegate = MessageDelegate()
        self.MessageDisp.setItemDelegate(delegate)

        # Set up model for messages
        self.model = QStandardItemModel()
        self.MessageDisp.setModel(self.model)

        # Connect send button to the send_message function
        self.SendButton.clicked.connect(self.send_message)
    def retrieve_messages(self):
        # Clear current messages in the display
        self.model.clear()
        
        try:
            # Query to select all messages from the database
            query = "SELECT sender, message, timestamp, sent FROM messages ORDER BY timestamp"
            cursor.execute(query)
            messages = cursor.fetchall()
            
            # Populate the message display widget with retrieved messages
            for sender, text, timestamp, is_received in messages:
                if isinstance(timestamp, str):
                    # Convert string timestamp to QDateTime
                    timestamp = QDateTime.fromString(timestamp, 'yyyy-MM-dd HH:mm:ss')
                
                # Create Message object
                message = Message(sender, text, timestamp, bool(is_received))
                
                # Determine if the message was sent by the user
                is_sent = sender == self.senderName
                self.add_message(message, is_sent)

            # Scroll to the bottom after all messages are loaded
            self.scroll_to_bottom()

        except con.Error as e:
            print(f"Error retrieving messages from database: {e}")
    
    def scroll_to_bottom(self):
    # Ensure the chat list is scrolled to the bottom
        scrollbar = self.MessageDisp.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
       
    def duplicate_table(self, original_table):
        new_table = QTableWidget()
        
        # Determine the last non-empty row
        last_row_with_data = -1
        for row in range(original_table.rowCount()):
            for column in range(original_table.columnCount()):
                if original_table.item(row, column) and original_table.item(row, column).text().strip():
                    last_row_with_data = row
                    break

        # Set the row and column count up to the last row with data
        new_table.setRowCount(last_row_with_data + 1)
        new_table.setColumnCount(original_table.columnCount())

        new_table.setHorizontalHeaderLabels(
            [original_table.horizontalHeaderItem(i).text() for i in range(original_table.columnCount())]
        )

        new_table.setVerticalHeaderLabels(
            [
                original_table.verticalHeaderItem(i).text() if original_table.verticalHeaderItem(i) else ""
                for i in range(last_row_with_data + 1)
            ]
        )

        for row in range(last_row_with_data + 1):
            for column in range(original_table.columnCount()):
                original_item = original_table.item(row, column)
                if original_item:
                    new_item = QTableWidgetItem(original_item.text())

                    new_item.setFont(original_item.font())
                    new_item.setTextAlignment(original_item.textAlignment())
                    new_item.setBackground(original_item.background())
                    new_item.setForeground(original_item.foreground())
                    new_item.setFlags(original_item.flags())
                    new_item.setToolTip(original_item.toolTip())
                    new_item.setStatusTip(original_item.statusTip())

                    # Set the new item in the new table
                    new_table.setItem(row, column, new_item)

        # Apply borders and alignments
        for row in range(new_table.rowCount()):
            for column in range(new_table.columnCount()):
                new_table.item(row, column).setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                new_table.item(row, column).setTextAlignment(Qt.AlignCenter)

        # Copy column widths
        for col in range(original_table.columnCount()):
            new_table.setColumnWidth(col, original_table.columnWidth(col))

        # Copy row heights
        for row in range(last_row_with_data + 1):
            new_table.setRowHeight(row, original_table.rowHeight(row))

        # Apply style sheet
        new_table.setStyleSheet("""
            /* General Table Styles */
            QTableWidget {
                gridline-color: #D6DBDF;
                background-color: #FFFFFF;
                alternate-background-color: #F7F9F9;
                font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
                font-size: 12pt;
                border: 1px solid #D6DBDF;
            }
            /* Header Styles */
            QHeaderView::section {
                background-color: #2C3E50;
                color: white;
                font-weight: bold;
                padding: 6px;
                border: 1px solid #D6DBDF;
                border-bottom: 2px solid #2980B9;
                text-align: center;
            }
            /* Cell Styles */
            QTableWidget::item {
                border-bottom: 1px solid #D6DBDF;
                padding: 6px;
                text-align: center;
            }
            /* Alternating Row Colors */
            QTableWidget::item:alternate {
                background-color: #F7F9F9;
            }
            /* Selected Cell Styles */
            QTableWidget::item:selected {
                background-color: #85C1E9;
                color: #FFFFFF;
            }
            /* First Column Left Border */
            QTableWidget::item {
                border-left: 1px solid #D6DBDF;
            }
            /* Scrollbar Styles */
            QScrollBar:vertical {
                background: #F0F3F4;
                width: 12px;
                margin: 18px 0 18px 0;
                border: 1px solid #D6DBDF;
            }
            QScrollBar::handle:vertical {
                background: #BDC3C7;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)

        new_table.setSelectionMode(QListWidget.NoSelection)
        return new_table

    def init_message_display(self):
        # Set item delegate for custom message display
        delegate = MessageDelegate()
        self.MessageDisp.setItemDelegate(delegate)

        # Set up model for messages
        self.model = QStandardItemModel()
        self.MessageDisp.setModel(self.model)

        # Connect send button to the send_message function
        self.SendButton.clicked.connect(self.send_message)
    def Messages(self):
        self.MessageArea.show()
        self.home.hide()
        self.EmployeeTable.hide()
        disp = self.MessageDisp
        
        self.model = QStandardItemModel()
        self.model = QStandardItemModel()
        disp.setModel(self.model)

        # Set item delegate
        delegate = MessageDelegate()
        disp.setItemDelegate(delegate)
        self.SendButton.clicked.connect(self.send_message)


        # Load messages from the database
        self.load_messages()

    def load_messages(self):
        cursor.execute("SELECT sender, message, timestamp FROM messages ORDER BY timestamp ASC")
        for sender, text, timestamp in cursor.fetchall():
            is_received = sender != self.senderName  # If the sender is not the current user, it was received
            message = Message(sender, text, QDateTime.fromString(str(timestamp), 'yyyy-MM-dd HH:mm:ss'), is_received)
            self.add_message(message)

    def add_message(self, message):
        item = QStandardItem(message.sender)
        item.setData(message, Qt.UserRole)  # Store message object
        self.model.appendRow([item])

    def send_message(self):
        self.admin_mail = "ananeheisler@gmail.com"
        
        text = self.MessageEdit.toPlainText()
        if text:  # Ensure the input is not empty
            timestamp = QDateTime.currentDateTime()
            # Add the sent message
            self.add_message(Message(self.senderName, text, timestamp, False))
            self.save_message(self.senderName, text, timestamp)

            self.MessageEdit.clear()
            # Define email parameters
            subject = self.branch_name
            body = text
            to_email = self.admin_mail
            from_email = "princekoomson03@gmail.com" 
            smtp_server = "smtp.gmail.com" 
            smtp_port = 587 
            smtp_user = "qwadjo739@gmail.com"
            smtp_password = "Qwadjo#0453"

            # Send the email
            self.send_email(subject, body, to_email, from_email, smtp_server, smtp_port, smtp_user, smtp_password)


    def receive_message(self, sender, text):
        timestamp = QDateTime.currentDateTime()
        self.add_message(Message(sender, text, timestamp, True))
        self.save_message(sender, text, timestamp)

    def save_message(self, sender, text, timestamp):

        cursor.execute("INSERT INTO messages (sender, message, timestamp) VALUES (%s, %s, %s)",
                       (sender, text, timestamp.toString('yyyy-MM-dd HH:mm:ss')))
        db.commit()


    def send_email(self, subject, body, to_email, from_email, smtp_server, smtp_port, smtp_user, smtp_password):
        # Create message container
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject

        # Attach the body with the msg instance
        msg.attach(MIMEText(body, 'plain'))

        # Initialize server to None
        server = None

        try:
            # Set up the server
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()  # Upgrade the connection to a secure encrypted SSL/TLS connection

            # Login to server
            server.login(smtp_user, smtp_password)

            # Send email
            server.sendmail(from_email, to_email, msg.as_string())
            print("Email sent successfully!")
        except Exception as e:
            print(f"Failed to send email: {e}")
        finally:
            if server is not None:
                # Quit the server if it was initialized
                server.quit()

    def send_email0(self, subject, body, to_email, from_email, smtp_server, smtp_port, smtp_user, smtp_password):
        # Create message container
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject

        # Attach the body with the msg instance
        msg.attach(MIMEText(body, 'plain'))

        try:
            # Set up the server
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()  # Upgrade the connection to a secure encrypted SSL/TLS connection

            # Login to server
            server.login(smtp_user, smtp_password)

            # Send email
            server.sendmail(from_email, to_email, msg.as_string())
            print("Email sent successfully!")
        except Exception as e:
            print(f"Failed to send email: {e}")
        finally:
            # Quit the server
            server.quit()


    def init_hover_effects(self):
        QTimer.singleShot(0, self.apply_hover_effects)
    def init_hover_effects(self):
        QTimer.singleShot(0, self.apply_hover_effects)
    def apply_hover_effects(self):
        button_names = ["Inventorybtn", "Storesbtn", "Employeesbtn", "Productsbtn", "Reportbtn", "LogOutbtn"]
        for name in button_names:
            btn = self.findChild(QToolButton, name)
            if btn:
                self.applyhover(btn)
            else:
                print(f"Button with objectName '{name}' not found")
    def applyhover(self, button):
        # Ensure button is not None
        if button is None:
            print("No button provided to apply hover effect.")
            return

        hover_animation = QPropertyAnimation(button, b"geometry")
        hover_animation.setDuration(300)
        hover_animation.setStartValue(button.geometry())
        hover_animation.setEndValue(button.geometry().adjusted(15, 0, 15, 0))  # Adjust size

        leave_animation = QPropertyAnimation(button, b"geometry")
        leave_animation.setDuration(300)
        leave_animation.setStartValue(button.geometry().adjusted(15, 0, 15, 0))
        leave_animation.setEndValue(button.geometry())

        def enter_event(event):
            hover_animation.start()
            super(button.__class__, button).enterEvent(event)

        def leave_event(event):
            leave_animation.start()
            super(button.__class__, button).leaveEvent(event)

        button.enterEvent = enter_event
        button.leaveEvent = leave_event

class AddStore(QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        main_dir = os.path.dirname(os.path.abspath(__file__))
        Ui = os.path.join(main_dir, 'Ui', 'AddStore.ui')
        loadUi(Ui, self)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.Cancel.clicked.connect(self.Closeform)
        self.Close.clicked.connect(self.Closeform)
        self.Confirm.clicked.connect(self.AddStore)    
    def AddStore(self):
        Name = self.BrName.text()
        Location = self.BrLoc.text()
        if len(Name) ==0 or len(Location)==0:
            self.Error.setText("Please input all fields!!")
        else:
            query = "SELECT * FROM branch WHERE Branch_name = %s"
            cursor.execute(query, (Name,))
            result = cursor.fetchone()
            if result:
                QMessageBox.critical(self, "Error", "Branch Name exists already")
            else:
                query = "INSERT INTO branch (Branch_name, Branch_location) VALUES (%s, %s)"
                values = (Name, Location)
                cursor.execute(query, values)
                db.commit()
                QMessageBox.information(self, "Success", "New store added successfully")
                invquery = f"ALTER TABLE inventory ADD COLUMN {Name} INT NOT NULL"
                cursor.execute(invquery)
                db.commit()
                
                self.Closeform()
    def Closeform(self):
        self.close()

class DelStore(QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        main_dir = os.path.dirname(os.path.abspath(__file__))
        Ui = os.path.join(main_dir, 'Ui', 'DelStore.ui')
        loadUi(Ui, self)
        #self.ui = loadUi("DelStore.ui",self)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.Confirm.clicked.connect(self.Del)
        self.Cancel.clicked.connect(self.Closeform)
        self.Close.clicked.connect(self.Closeform)

    def Del(self):
        Name = self.BrName.text()
        Location = self.BrLoc.text()
        if len(Name) == 0 or len(Location)==0:
            self.Error.setText("Please input all fields!")
        else:
            query = "SELECT * FROM branch WHERE Branch_name = %s"
            cursor.execute(query, (Name,))
            result = cursor.fetchone()
            if result:
                query = "DELETE FROM branch WHERE Branch_name = %s"
                cursor.execute(query, (Name,))
                db.commit()
                invquery = f"ALTER TABLE inventory DROP COLUMN {Name}"
                cursor.execute(invquery)
                db.commit()
                QMessageBox.information(self, "Success", "Branch deleted successfully")
                self.Closeform()
            else:
                QMessageBox.critical(self, "Error", "Branch does not exist")

    
    def Closeform(self):
        self.close()

class AddEmployee(QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        main_dir = os.path.dirname(os.path.abspath(__file__))
        Ui = os.path.join(main_dir, 'Ui', 'AddEmp.ui')
        loadUi(Ui, self)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.Confirm.clicked.connect(self.AddEmp)
        self.Cancel.clicked.connect(self.Closeform)
        self.Close.clicked.connect(self.Closeform)

        
        gen_group = QButtonGroup(self)
        gen_group.addButton(self.MaleCheck)
        gen_group.addButton(self.FemaleCheck)
        gen_group.setExclusive(True)
        pos_group = QButtonGroup(self)
        pos_group.addButton(self.ManCheck)
        pos_group.addButton(self.SalesPCheck)
        pos_group.setExclusive(True)
        self.Gender = ""
        self.position =""
        self.GenAndPos()

        self.StoCombo.lineEdit().setPlaceholderText("--select or search--")
        self.StoCombo.completer().setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
        brquery = "SELECT Branch_name FROM branch"
        cursor.execute(brquery)
        prods = cursor.fetchall()
        self.StoCombo.addItem(None)
        for item in prods:
            self.StoCombo.addItem(item[0])

    def GenAndPos(self):
        if self.MaleCheck.isChecked():
            self.Gender = "M"
        if self.FemaleCheck.isChecked():
            self.Gender = "F"
        if self.SalesPCheck.isChecked():
            self.position= "Salesperson"
        if self.ManCheck.isChecked():
            self.position = "Manager"

    def AddEmp0(self):
        FName = self.Fname.text()
        LName = self.Lname.text()
        Name = f"{FName} {LName}"
        Email = self.Email.text()
        Phone = self.Phone.text()
        self.GenAndPos()

        Branch = self.StoCombo.currentText()
        date = self.AddDate.date()
        Date = date.toString("yyyy-MM-DD")

        if len(FName) == 0 or len(LName) == 0 or len(Email) == 0 or len(Phone) == 0 or self.StoCombo.currentText() =="":
            self.Error.setText("Please input all fields!")
        else:
            if len(Phone) != 10:
                self.Error.setText("Invalid phone number!")
            else:
                self.Error.clear()
                if self.Gender =="" or self.position == "":
                    self.Error.setText("Please select gender or position!")
                else:
                    if self.position == "Salesperson":
                        query = "SELECT * FROM salespersons WHERE Email = %s;"
                        cursor.execute(query, (Email,))
                        result = cursor.fetchone()
                        if result:
                            QMessageBox.warning(None, "Warning", "User exists already.")
                        else:
                            # Generate a random password
                            alphabet = string.ascii_letters + string.digits
                            Pword = ''.join(secrets.choice(alphabet) for _ in range(8))

                            # Hash the password using bcrypt
                            #hashed_password = bcrypt.hashpw(Pword.encode('utf-8'), bcrypt.gensalt())
                            hashed_password = hashlib.sha256(Pword.encode('utf-8')).hexdigest()

                            # Insert the new user into the database
                            query = "INSERT INTO salespersons (First_name, Last_name, Email, Phone, Branch_Name, Date_of_birth, Gender, Password) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                            values = (FName, LName, Email, Phone, Branch, Date, self.Gender, hashed_password)
                            cursor.execute(query, values)
                            db.commit()

                        QMessageBox.information(None, "Success", f"Employee added successfully.\nGenerated Password: {Pword}")
                        self.Closeform()
                    elif self.position == "Manager":
                        query = "SELECT * FROM managers WHERE Email = %s;"
                        cursor.execute(query, (Email,))
                        result = cursor.fetchone()
                        if result:
                            QMessageBox.warning(None, "Warning", "User exists already.")
                        else:
                            # Generate a random password
                            alphabet = string.ascii_letters + string.digits
                            Pword = ''.join(secrets.choice(alphabet) for _ in range(8))

                            # Hash the password using bcrypt
                            #hashed_password = bcrypt.hashpw(Pword.encode('utf-8'), bcrypt.gensalt())
                            hashed_password = hashlib.sha256(Pword.encode('utf-8')).hexdigest()

                            # Insert the new user into the database
                            query = """
                                INSERT INTO managers (
                                    First_name, Last_name, Email, Phone, Branch_Name, 
                                    Date_of_birth, Gender, Password
                                ) 
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            """
                            values = (FName, LName, Email, Phone, Branch, Date, self.Gender, hashed_password)
                            cursor.execute(query, values)
                            db.commit()

                        QMessageBox.information(None, "Success", f"Employee added successfully.\nGenerated Password: {Pword}")
                        self.Closeform()


    def AddEmp(self):
        FName = self.Fname.text()
        LName = self.Lname.text()
        Name = f"{FName} {LName}"
        Email = self.Email.text()
        Phone = self.Phone.text()
        self.GenAndPos()

        Branch = self.StoCombo.currentText()
        date = self.AddDate.date()
        Date = date.toString("yyyy-MM-dd")

        # Regex pattern for validating email
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        if len(FName) == 0 or len(LName) == 0 or len(Email) == 0 or len(Phone) == 0 or self.StoCombo.currentText() == "":
            self.Error.setText("Please input all fields!")
        else:
            if len(Phone) != 10 or not Phone.isdigit():
                self.Error.setText("Invalid phone number! It should be 10 digits.")
            elif not re.match(email_pattern, Email):
                self.Error.setText("Invalid email format!")
            else:
                self.Error.clear()
                if self.Gender == "" or self.position == "":
                    self.Error.setText("Please select gender or position!")
                else:
                    # Check if user exists in the respective table
                    table = "salespersons" if self.position == "Salesperson" else "managers"
                    query = f"SELECT * FROM {table} WHERE Email = %s;"
                    cursor.execute(query, (Email,))
                    result = cursor.fetchone()
                    
                    if result:
                        QMessageBox.warning(None, "Warning", "User already exists.")
                    else:
                        # Generate a random password
                        alphabet = string.ascii_letters + string.digits
                        Pword = ''.join(secrets.choice(alphabet) for _ in range(8))

                        # Hash the password using SHA-256
                        hashed_password = hashlib.sha256(Pword.encode('utf-8')).hexdigest()

                        # Insert the new user into the database
                        query = f"""
                            INSERT INTO {table} (
                                First_name, Last_name, Email, Phone, Branch_Name, 
                                Date_of_birth, Gender, Password
                            ) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """
                        values = (FName, LName, Email, Phone, Branch, Date, self.Gender, hashed_password)
                        cursor.execute(query, values)
                        db.commit()

                        QMessageBox.information(None, "Success", f"Employee added successfully.\nGenerated Password: {Pword}")
                        self.Closeform()

                                   
    def Closeform(self):
        self.close()

class EditEmployee(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        main_dir = os.path.dirname(os.path.abspath(__file__))
        Ui = os.path.join(main_dir, 'Ui', 'EditEmp.ui')
        loadUi(Ui, self)
        
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.Confirm.clicked.connect(self.EditEmp)
        self.Cancel.clicked.connect(self.Closeform)
        self.Close.clicked.connect(self.Closeform)
        self.NewPassButton.clicked.connect(self.NewPass)

        # Set up the combo box with a placeholder and completion mode
        self.EmpCombo.lineEdit().setPlaceholderText("--select or search--")
        self.EmpCombo.completer().setCompletionMode(QtWidgets.QCompleter.PopupCompletion)

        # Query to fetch employee names
        empsquery = """
            SELECT Email FROM managers
            UNION
            SELECT Email FROM salespersons;
        """
        cursor.execute(empsquery)
        emps = cursor.fetchall()
        
        # Add a placeholder item (empty string) to the combo box
        self.EmpCombo.addItem("")
        for emp in emps:
            self.EmpCombo.addItem(emp[0])
        
        self.EmpCombo.currentIndexChanged.connect(self.EmpInfo)
        brquery = "SELECT Branch_name FROM branch"
        cursor.execute(brquery)
        store = cursor.fetchall()
        for item in store:
            self.StoCombo.addItem(item[0])

    def EmpInfo(self):
        Email = self.EmpCombo.currentText()
        Emailquery = '''
            SELECT CONCAT(First_name, " ", Last_name) FROM salespersons WHERE Email = %s
            UNION
            SELECT CONCAT(First_name, " ", Last_name) FROM managers WHERE Email = %s
        '''
        cursor.execute(Emailquery, (Email, Email))
        Name = cursor.fetchone()[0]
        Fname, Lname = Name.split()
        Phonequery = '''
            SELECT Phone FROM salespersons WHERE Email = %s
            UNION
            SELECT Phone FROM managers WHERE Email = %s
        '''
        cursor.execute(Phonequery, (Email, Email))
        Phone = cursor.fetchone()[0]
        
        brquery = "SELECT Branch_name FROM salespersons WHERE Email = %s UNION SELECT Branch_name FROM managers WHERE Email = %s"
        cursor.execute(brquery, (Email, Email))
        store = cursor.fetchall()

        if store:
            branch_name = store[0][0]
            self.StoCombo.setCurrentText(branch_name)

        self.FnameEdit.setText(Fname)
        self.LnameEdit.setText(Lname)
        self.PhoneEdit.setText(str(Phone))

    def EditEmp(self):
        Email = self.EmpCombo.currentText()
        Fname = self.FnameEdit.text()
        Lname = self.LnameEdit.text()
        Phone = self.PhoneEdit.text()
        Branch = self.StoCombo.currentText()

        # Regex pattern for validating phone number
        phone_pattern = r'^\d{10}$'

        # Validate input fields
        if not Email or not Fname or not Lname or not Phone or not Branch:
            QMessageBox.warning(self, "Input Error", "Please fill out all fields.")
            return

        if not re.match(phone_pattern, Phone):
            QMessageBox.warning(self, "Input Error", "Invalid phone number! It should be 10 digits.")
            return

        try:
            # Update query for both salespersons and managers
            update_query = '''
                UPDATE salespersons
                SET First_name = %s, Last_name = %s, Phone = %s, Branch_Name = %s
                WHERE Email = %s;
            '''
            cursor.execute(update_query, (Fname, Lname, Phone, Branch, Email))
            
            # Check if the employee was updated in the salespersons table, if not update in managers table
            if cursor.rowcount == 0:
                update_query = '''
                    UPDATE managers
                    SET First_name = %s, Last_name = %s, Phone = %s, Branch_Name = %s
                    WHERE Email = %s;
                '''
                cursor.execute(update_query, (Fname, Lname, Phone, Branch, Email))

            db.commit()

            QMessageBox.information(self, "Success", "Employee information updated successfully.")
            self.Closeform()

        except Exception as e:
            db.rollback()  # Roll back any changes if there's an error
            QMessageBox.critical(self, "Database Error", f"An error occurred: {str(e)}")


    def NewPass(self):
        Email = self.EmpCombo.currentText()

        if not Email:
            QMessageBox.warning(self, "Input Error", "Please select an employee.")
            return

        try:
            # Generate a new random password
            alphabet = string.ascii_letters + string.digits
            new_password = ''.join(secrets.choice(alphabet) for _ in range(8))

            # Hash the password using SHA-256
            hashed_password = hashlib.sha256(new_password.encode('utf-8')).hexdigest()

            # Update the password in the database (first try in salespersons, then managers)
            update_query = '''
                UPDATE salespersons
                SET Password = %s
                WHERE Email = %s;
            '''
            cursor.execute(update_query, (hashed_password, Email))

            # If no rows were affected, try updating in the managers table
            if cursor.rowcount == 0:
                update_query = '''
                    UPDATE managers
                    SET Password = %s
                    WHERE Email = %s;
                '''
                cursor.execute(update_query, (hashed_password, Email))

            db.commit()

            # Inform the user of the new password
            QMessageBox.information(self, "Success", f"New password generated: {new_password}")

        except Exception as e:
            db.rollback()
            QMessageBox.critical(self, "Database Error", f"An error occurred: {str(e)}")


    def Closeform(self):
        self.close()
    #delete employee calss0
class DelEmployee(QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        main_dir = os.path.dirname(os.path.abspath(__file__))
        Ui = os.path.join(main_dir, 'Ui', 'DelEmp.ui')
        loadUi(Ui, self)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        #Buttons
        self.Confirm.clicked.connect(self.DelEmp)
        self.Cancel.clicked.connect(self.Closeform)
        self.Close.clicked.connect(self.Closeform)

        self.EmpCombo.lineEdit().setPlaceholderText("--select or search--")
        self.EmpCombo.completer().setCompletionMode(QtWidgets.QCompleter.PopupCompletion)

        # Fetch employees
        empquery = "SELECT CONCAT(First_name, ' ', Last_name) FROM managers UNION SELECT CONCAT(First_name, ' ', Last_name) FROM salespersons;"
        cursor.execute(empquery)
        allemps = cursor.fetchall()

        # Add None as the first item
        self.EmpCombo.addItem(None)
        for item in allemps:
            self.EmpCombo.addItem(item[0])
        self.EmpCombo.currentIndexChanged.connect(self.SelEmp)

        #Branches
        self.BrCombo.lineEdit().setPlaceholderText("--select or search--")
        self.BrCombo.completer().setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
        brquery = "SELECT CONCAT(Branch_name, ', ', Branch_location) FROM branch"
        cursor.execute(brquery)
        branches = cursor.fetchall()
        self.BrCombo.addItem(None)
        for item in branches:
            self.BrCombo.addItem(item[0])
        self.BrCombo.currentIndexChanged.connect(self.SelEmp2)
    def SelEmp(self):
        name = self.EmpCombo.currentText()
        if name:
            first_name, last_name = name.split()
            # Query for managers
            manquery = "SELECT Branch_name FROM managers WHERE First_name = %s AND Last_name = %s"
            cursor.execute(manquery, (first_name, last_name))
            branch = cursor.fetchone()
            if branch:
                self.BrCombo.clear()
                #self.BrCombo.addItem(None)
                self.BrCombo.addItem(branch[0])
            else:
                # Query for salespersons if not found in managers
                empquery = "SELECT Branch_name FROM salespersons WHERE First_name = %s AND Last_name = %s"
                cursor.execute(empquery, (first_name, last_name))
                result = cursor.fetchone()
                
                if result:
                    self.BrCombo.clear()
                    self.BrCombo.addItem(result[0])
    def SelEmp2(self):
        branch = self.BrCombo.currentText()
        if branch:
            parts = branch.split(', ')
            if len(parts) == 2:
                brname, brloc = parts
                self.EmpCombo.clear()
                self.EmpCombo.addItem(None)
                # Query for employees in managers and salespersons
                query = "SELECT CONCAT(First_name, ' ', Last_name) FROM managers WHERE Branch_name = %s UNION SELECT CONCAT(First_name, ' ', last_name) FROM salespersons WHERE Branch_name = %s;"
                cursor.execute(query, (brname, brname))
                allemps = cursor.fetchall()
                
                
                if allemps:
                    for item in allemps:
                        self.EmpCombo.addItem(item[0])
    def DelEmp(self):
        Name = self.EmpCombo.currentText()
        first_name, last_name = Name.split()
        Branch = self.BrCombo.currentText()
        if Name and Branch:
            query = "SELECT * FROM managers WHERE First_name = %s AND Last_name = %s AND Branch_name = %s"
            cursor.execute(query, (first_name, last_name, Branch))
            result = cursor.fetchone()
            if result:
                query = "DELETE FROM managers WHERE First_name = %s AND Last_name = %s AND Branch_name = %s"
                cursor.execute(query, (first_name, last_name, Branch))
                db.commit()
                #Update branches
                query2 = "UPDATE branch SET Branch_Manager = '' WHERE Branch_Manager = %s AND Branch_name = %s"
                cursor.execute(query2, (Name, Branch))
                db.commit()
            else:
                query = "SELECT * FROM salespersons WHERE First_name = %s AND Last_name = %s AND Branch_name = %s"
                cursor.execute(query, (first_name, last_name, Branch))
                result = cursor.fetchone()
                if result:
                    query = "DELETE FROM salespersons WHERE First_name = %s AND Last_name = %s AND Branch_name = %s"
                    cursor.execute(query, (first_name, last_name, Branch))
                    db.commit()
            QMessageBox.information(None, "Success", "Employee deleted sucessfully!")
            self.Closeform()
        else:
            QMessageBox.warning(None, "Warning", "User does not exist.")
    def Closeform(self):
        self.close()

class AddProduct(QDialog):
    image = None
    def __init__(self, parent = None):
        super().__init__(parent)
        main_dir = os.path.dirname(os.path.abspath(__file__))
        Ui = os.path.join(main_dir, 'Ui', 'AddPro.ui')
        loadUi(Ui, self)

        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.Confirm.clicked.connect(self.AddPro)
        self.Cancel.clicked.connect(self.Closeform)
        self.Close.clicked.connect(self.Closeform)
        self.PickImg.clicked.connect(self.selectImg)
    
    def selectImg(self):
        filediag = QFileDialog(self)
        filediag.setFileMode(QFileDialog.ExistingFile)
        filediag.setNameFilter("Image Files (*.png *.jpg *.jpeg *.webp)")
        if not self.ImgName.text():
            if filediag.exec_():
                file = filediag.selectedFiles()
                imgfile = file[0]
                file_name = os.path.basename(imgfile)
                AddProduct.prime = file_name
                #print(AddProduct.prime)
                self.ImgName.setText(file_name)
            with open(imgfile, 'rb') as dbfile:
                imgdata = dbfile.read()
                #self.image = imgdata
                AddProduct.image = imgdata
        

   
    def Closeform(self):
        self.close()
    def AddPro(self):
        Name = self.Name.text()
        Details = self.Details.toPlainText()
        picname = self.ImgName.text()
        img = AddProduct.image

        if len(Name) == 0 or len(Details) == 0:
            self.Error.setText("Please input all fields!")
        else:
            query = "SELECT * FROM Products WHERE Product_name = %s"
            cursor.execute(query, (Name,))
            result = cursor.fetchone()
            if result:
                QMessageBox.critical(self, "Error", "Product exists already")
            else:
                # Insert the product with the image
                query = "INSERT INTO Products (Product_name, Product_details, Product_image) VALUES (%s, %s, %s)"
                values = (Name, Details, img)
                cursor.execute(query, values)
                db.commit()

                QMessageBox.information(None, "Success", "Product added successfully")
                self.Closeform()

    def AddPro0(self):
        Name = self.Name.text()
        Details = self.Details.toPlainText()
        Price = self.Price.text()
        picname = self.ImgName.text()
        #gym = self.image
        img = AddProduct.image
        if picname:
            img = AddProduct.image
        if len(Name) == 0 or len(Details) == 0 or len(Price) ==0:
            self.Error.setText("Please input all fields!")
        else:
            query = "select * from Products where Product_name = '"+Name+"'"
            cursor.execute(query)
            result = cursor.fetchone()
            if result:
                QMessageBox.critical(self, "Error", "Product exists already")
            else:
                query = "INSERT INTO Products (Product_name, Product_details) values (%s, %s)"#, %s)"#, %s)"
                values = (Name, Details)#, img)
                cursor.execute(query, values)
                db.commit()
                #Update Inv table
                #query3 = "INSERT INTO inventory (Product_name, Total) VALUES (%s, %s)"
                #values3 = (Name, "0")
                #cursor.execute(query3, values3)
                #db.commit()
                QMessageBox.information(None, "Success", "Product added successfully")
                self.Closeform()
                #print(AddProduct.image)

class DelProduct(QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        main_dir = os.path.dirname(os.path.abspath(__file__))
        Ui = os.path.join(main_dir, 'Ui', 'DelPro.ui')
        loadUi(Ui, self)
        #self. ui = loadUi("DelPro.ui",self)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.Confirm.clicked.connect(self.DelProduct)
        self.Cancel.clicked.connect(self.Closeform)
        self.Close.clicked.connect(self.Closeform)
    def Closeform(self):
        self.close()
    
    def DelProduct(self):
        Name = self.Name.text()
        if len(Name) == 0:
            self.Error.setText("Please input product name!")
        else:
            query = "select Product_ID from Products where Product_name = '"+Name+"'"
            cursor.execute(query)
            result = cursor.fetchone()
            if result:
                #ID = str(result[0])
                query = "delete from Products where Product_name = '"+Name+"'"
                cursor.execute(query)
                db.commit()
                QMessageBox.information(None, "Success", "Product deleted successfully")
                self.Closeform()
            else:
                QMessageBox.critical(self, "Error", "Product does not exist")

class AddInv(QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        main_dir = os.path.dirname(os.path.abspath(__file__))
        Ui = os.path.join(main_dir, 'Ui', 'AddInv.ui')
        loadUi(Ui, self)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.Confirm.clicked.connect(self.addinv)
        self.Cancel.clicked.connect(self.closeform)
        self.Close.clicked.connect(self.closeform)
        #self.PName.editingFinished.connect(self.FindPro)
        self.Qty.setValidator(QIntValidator(1, 100000))
        self.InvPriceBox.hide()


        self.ProCombo.lineEdit().setPlaceholderText("--select or search--")
        self.ProCombo.completer().setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
        proquery = "SELECT Product_name FROM Products"
        cursor.execute(proquery)
        prods = cursor.fetchall()
        self.ProCombo.addItem(None)
        for item in prods:
            self.ProCombo.addItem(item[0])
        self.ProCombo.currentIndexChanged.connect(self.SelPro)
        
        #storage combo elements
        storage = ["128 GB", "256 GB", "512 GB", "1 TB", "2 TB"]
        self.StoCombo.clear()  # Clear existing 
        self.StoCombo.addItem("--Select--")
        for item in storage:
            self.StoCombo.addItem(item)
        self.StoCombo.currentIndexChanged.connect(self.SpecificProduct)

        #ram combo elements
        ram = ["4 GB","8 GB", "12 GB", "16 GB"]

        self.RamCombo.clear()  # Clear existing items
        self.RamCombo.addItem("--select--")
        for item in ram:
            self.RamCombo.addItem(item)
        self.RamCombo.currentIndexChanged.connect(self.SpecificProduct)

    def SelPro(self):
        PName = self.ProCombo.currentText()
        Ram = self.RamCombo.currentText()
        Storage = self.StoCombo.currentText()
        if PName == "":
            self.Error.setText("Please select Product")
        else:
            self.Error.setText("")
            if Ram !="--select--" or Storage !="--select--":
                query = "SELECT Spec_ID FROM specificproducts WHERE Product_name = %s AND Ram = %s AND Storage = %s"
                cursor.execute(query, (PName, Ram, Storage))
                result = cursor.fetchone()
                if result:
                    ID = result[0]
                    invquery = "SELECT In_Stock FROM inventory WHERE Spec_ID = %s"
                    cursor.execute(invquery, (ID,))
                    invresult = cursor.fetchone()
                    if invresult:
                        self.InStock.setText(str(invresult[0]))
                else:
                    self.InStock.setText("N/A")
            else:
                self.Error.setText("Please select RAM and Storage")
            
        # Connect signals
        self.RamCombo.currentIndexChanged.connect(self.SpecificProduct)
        self.StoCombo.currentIndexChanged.connect(self.SpecificProduct)

    def SpecificProduct(self):
        PName = self.ProCombo.currentText()
        Ram = self.RamCombo.currentText()
        Storage = self.StoCombo.currentText()

        if Ram !="--select--" or Storage !="--select--":
            query = "SELECT Spec_ID FROM specificproducts WHERE Product_name = %s AND Ram = %s AND Storage = %s"
            cursor.execute(query, (PName, Ram, Storage))
            result = cursor.fetchone()
            if result:
                ID = result[0]
                invquery = "SELECT In_Stock FROM inventory WHERE Spec_ID = %s"
                cursor.execute(invquery, (ID,))
                invresult = cursor.fetchone()
                if invresult:
                    self.InStock.setText(str(invresult[0]))
                    #instock = int(self.InStock.text()) + int(self.Qty.text())
                    #self.NewQty.setText(str(instock))
            #else:
                #self.InStock.setText("N/A")

        self.Qty.textChanged.connect(self.NQty)
    def NQty(self):
        instock = self.InStock.text()
        if instock !="N/A":
            qty = self.Qty.text()
            if qty !="":
                newqty = int(qty) + int(instock)
                self.NewQty.setText(str(newqty))
        else:
            self.NewQty.setText(instock)

    def closeform(self):
        self.close()
    def addinv(self):
        PName = self.ProCombo.currentText()
        ram = self.RamCombo.currentText()
        storage = self.StoCombo.currentText()
        newqty = self.NewQty.text()

        if PName and ram and storage and newqty!= "":
            query = "SELECT Spec_ID FROM specificproducts WHERE Product_name = %s AND Ram = %s AND Storage =%s"
            cursor.execute(query, (PName, ram, storage))
            result = cursor.fetchone()
            if result:
                ID = result[0]
                query = "UPDATE inventory SET In_Stock = %s WHERE Spec_ID = %s"
                cursor.execute(query, (newqty, ID))
                db.commit()
                QMessageBox.information(None, "Success", "Inventory added successfully")
                self.close()
            else:
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("Choose an Action")
                msg_box.setText("Specified computer not available!\nPlease add price to add your new spec.")

                # Add two buttons with different functions
                button1 = msg_box.addButton("Yes", QMessageBox.ActionRole)
                button2 = msg_box.addButton("No", QMessageBox.ActionRole)

                button1.clicked.connect(self.proceed)
                button2.clicked.connect(self.dontproceed)
                
                msg_box.exec_()
        else:
            self.Error.setText("Please specify product and quantity to add")
    
    def proceed(self):
            self.InvPriceBox.show()
            self.InvPrice.setValidator(QDoubleValidator(0.00, 99999.99, 2))

            pname = self.ProCombo.currentText()
            ram = self.RamCombo.currentText()
            storage = self.StoCombo.currentText()
            price = self.InvPrice.text()
            qty = self.Qty.text()
            if price:
                query = "INSERT INTO specificproducts (Product_name, Ram, Storage, Price) values (%s, %s, %s, %s)"
                cursor.execute(query, (pname, ram, storage, price))
                db.commit()
                sidquery = "SELECT Spec_ID FROM specificproducts WHERE Product_name = %s AND Ram = %s AND Storage = %s"
                cursor.execute(sidquery, (pname, ram, storage))
                sid = cursor.fetchone()[0]
                invquery = "INSERT INTO inventory (Spec_ID, In_Stock) VALUES (%s, %s)"
                cursor.execute(invquery, (sid, qty))
                #upinv = ""
                QMessageBox.information(None, "Success", "Inventory added successfully")
            else:
                self.Error.setText("Please specify price for your new spec")

                
    def dontproceed(self):
        self.Error.setText("Item not found")
                    
class ManInv(QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        main_dir = os.path.dirname(os.path.abspath(__file__))
        Ui = os.path.join(main_dir, 'Ui', 'ManInv.ui')
        loadUi(Ui, self)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        #self.Confirm.clicked.connect(self.distribute)
        #def ManInv(self):
        proquery = "SELECT Product_name FROM Products"
        cursor.execute(proquery)
        prods = cursor.fetchall()
        for item in prods:
            self.ProCombo.addItem(item[0])
        stoquery = "SELECT Branch_name From branch"
        cursor.execute(stoquery)
        stores = cursor.fetchall()
        for item in stores:
            self.StoCombo.addItem(item[0])
        self.Qty.setValidator(QIntValidator(1, 100000))
        self.StoCombo.setEnabled(False)
        self.ProCombo.currentIndexChanged.connect(self.SelPro)
        self.StoCombo.currentIndexChanged.connect(self.SelSto)

        self.Confirm.clicked.connect(self.distribute)
        self.Close.clicked.connect(self.closeform)
        self.Cancel.clicked.connect(self.closeform)
    def SelPro(self):
        self.StoCombo.setEnabled(True)
        PName = self.ProCombo.currentText()
        #query = "SELECT ProductID FROM Products WHERE ProductName = '"+PName+"'"
        #cursor.execute(query)
        #ProID = cursor.fetchone()
        query2 = "SELECT `In_stock` FROM inventory WHERE Product_name = '"+PName+"'"#str(ProID[0])+"'"
        cursor.execute(query2)
        ProQty = cursor.fetchone()
        self.StockQty.setText(str(ProQty[0]))
    def SelSto(self):
        PName = self.ProCombo.currentText()
        SName = self.StoCombo.currentText()
        #query = "SELECT ProductID FROM Products WHERE ProductName = '"+PName+"'"
        #cursor.execute(query)
        #ProID = cursor.fetchone()
        query = "SELECT `"+SName+"` FROM inventory WHERE Product_name = '"+PName+"'"#str(ProID[0])+"'"
        cursor.execute(query)
        StoQty = cursor.fetchone()
        self.StoreQty.setText(str(StoQty[0]))

    def distribute(self):
        PName = self.ProCombo.currentText()
        SName = self.StoCombo.currentText()
        Qty = self.Qty.text()
        stockqty = self.StockQty.text()
        storeqty = self.StoreQty.text()
        if Qty == '':
            self.Error.setText("Please Enter Quantity to distribute")
        elif int(Qty) > int(stockqty):
            self.Error.setText("Quantity to distribute is more than the stock")
        else:
            Newstoreqty = int(storeqty) + int(Qty)
            Newstockqty = int(stockqty) - int(Qty)
            upquery = f"UPDATE inventory SET {SName} = %s, In_stock = %s WHERE Product_name = %s"
            #f"UPDATE inventory SET `{SName}` = %s, In_stock = %s WHERE Product_name = %s"
            cursor.execute(upquery, (Newstoreqty, Newstockqty, PName))
            db.commit()
            QMessageBox.information(None, "Success", "Product distributed successfully")
        #self.Error.setText(PName)
        #self.ref()
    def closeform(self):
        self.ref()
        self.close()
    def ref(self = ADboard):
        adboard = ADboard()
        adboard.refreshInv()

class Reporting:
    def __init__(self):
        # Initialize the figure and axes here if needed
        self.fig = Figure()

    def line_chart(self, data, x_col, y_col, title=None, x_label=None, y_label=None):
        ax1 = self.fig.add_subplot(111)
        ax1.plot(data[x_col], data[y_col], marker='o')
        if title:
            ax1.set_title(title)
        if x_label:
            ax1.set_xlabel(x_label)
        if y_label:
            ax1.set_ylabel(y_label)
        
        ax1.set_xticklabels([])  # Hide x-tick labels if needed
        ax1.set_yticklabels([])  # Hide y-tick labels if needed

        canvas = FigureCanvas(self.fig)
        return canvas
    def line_chart0(self, data, x_col, y_col, title='', x_label='', y_label=''):
        
        ax1 = self.fig.add_subplot(111)
        ax1.plot(data[x_col], data[y_col], marker='o')

        if title:
            ax1.set_title(title)
        if x_label:
            ax1.set_xlabel(x_label)
        if y_label:
            ax1.set_ylabel(y_label)

        # Set x-axis labels to display dates only
        x_labels = [str(x.date()) if hasattr(x, 'date') else str(x) for x in data[x_col]]
        ax1.set_xticks(data[x_col])
        ax1.set_xticklabels(x_labels, rotation=45, ha='right', fontsize = 8)

        # Set y-axis labels to display figures only
        y_labels = [str(y) for y in data[y_col]]
        ax1.set_yticks(data[y_col])
        ax1.set_yticklabels(y_labels, fontsize = 8)

        self.fig.subplots_adjust(left=0.15, right=0.85, top=0.85, bottom=0.25)
        self.fig.tight_layout()
        # Redraw the figure
        self.fig.canvas.draw_idle()

        canvas = FigureCanvas(self.fig)
        return canvas
    
    def bar_chart(self, data, x_col, y_col, title=None, x_label=None, y_label=None):
        ax2 = self.fig.add_subplot(111)
        ax2.bar(data[x_col], data[y_col])

        if title:
            ax2.set_title(title)
        if x_label:
            ax2.set_xlabel(x_label)
        if y_label:
            ax2.set_ylabel(y_label)

        # Format x-axis labels for dates
        x_labels = [str(x.date()) if hasattr(x, 'date') else str(x) for x in data[x_col]]
        ax2.set_xticks(data[x_col])
        ax2.set_xticklabels(x_labels, rotation=45, ha='right', fontsize=8)

        # Automatic y-axis ticks
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{int(y):,}'))

        # Adjust margins to minimize the drawing space
        self.fig.subplots_adjust(left=0.15, right=0.85, top=0.85, bottom=0.25)
        self.fig.tight_layout()
        self.fig.canvas.draw_idle()

        canvas = FigureCanvas(self.fig)
        return canvas

class Message:
    def __init__(self, sender, text, timestamp, is_received):
        self.sender = sender
        self.text = text
        self.timestamp = timestamp
        self.is_received = is_received

class MessageDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        model = index.model()
        message = model.data(index, Qt.UserRole)

        # Set font and colors based on is_received
        font = QFont()
        painter.setFont(font)

        # Define the padding, bubble color, and text color
        padding = 10
        bubble_color = QColor(0, 122, 255) if not message.is_received else QColor(230, 230, 230)
        text_color = QColor(255, 255, 255) if not message.is_received else QColor(0, 0, 0)

        # Calculate the text rectangle size
        text_rect = painter.boundingRect(option.rect, Qt.AlignLeft | Qt.AlignVCenter, message.text)
        text_rect = text_rect.adjusted(-padding, -padding, padding, padding)

        # Calculate the bubble rectangle size
        if message.is_received:
            bubble_rect = QRect(option.rect.left() + option.rect.width() - text_rect.width() - 20,  # Align right
                                option.rect.top() + 10,
                                text_rect.width() + 20,
                                text_rect.height() + 10)
        else:
            bubble_rect = QRect(option.rect.left() + 10,  # Align left
                                option.rect.top() + 10,
                                text_rect.width() + 20,
                                text_rect.height() + 10)

        # Draw the bubble background
        painter.setBrush(bubble_color)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(bubble_rect, 15, 15)

        # Draw the message text inside the bubble
        painter.setPen(text_color)
        painter.drawText(bubble_rect.adjusted(padding, padding, -padding, -padding),
                         Qt.AlignLeft | Qt.AlignVCenter,
                         message.text)
    def sizeHint(self, option, index):
        # Adjust size hint based on message length
        model = index.model()
        message = model.data(index, Qt.UserRole)
        text_rect = QFontMetrics(option.font).boundingRect(0, 0, option.rect.width() - 40, 0, Qt.TextWordWrap, message.text)
        return QSize(option.rect.width(), text_rect.height() + 30)

class DistributionAI:
    def __init__(self, data):
        self.data = data

    def analyze_line_chart(self, x_col, y_col):
        # Calculate the trend using the rolling average
        rolling_mean = self.data[y_col].rolling(window=5).mean()

        # Determine the trend direction
        if rolling_mean.iloc[-1] > rolling_mean.iloc[0]:
            recommendation = "Sales show an upward trend. Consider increasing stock or distribution."
        elif rolling_mean.iloc[-1] < rolling_mean.iloc[0]:
            recommendation = "Sales show a downward trend. Consider reducing stock or distribution."
        else:
            recommendation = "Sales are stable. Maintain current distribution levels."

        # Plot the original data and the trend line
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.plot(self.data[x_col], self.data[y_col], marker='o', label='Sales')
        ax.plot(self.data[x_col], rolling_mean, color='orange', label='Trend (Rolling Mean)')
        ax.set_title('Sales Trend Analysis')
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.legend()
        ax.grid(True)
        #plt.show()

        return fig, recommendation

    def analyze_brabar_chart(self, x_col, y_col):
        # Calculate the total and proportional sales
        total_sales = self.data[y_col].sum()
        proportional_sales = self.data[y_col] / total_sales
        
        # Identify branches with extreme values
        highest_sales_branch = self.data.loc[self.data[y_col].idxmax(), x_col]
        lowest_sales_branch = self.data.loc[self.data[y_col].idxmin(), x_col]
        
        recommendation = (
            f"Branch {highest_sales_branch} has the highest sales. "
            f"Consider increasing distribution here.\n"
            f"Branch {lowest_sales_branch} has the lowest sales. "
            f"Consider reducing distribution or investigating potential issues."
        )
        
        # Plot the bar chart
        fig, ax = plt.subplots(figsize=(6, 7))
        ax.bar(self.data[x_col], self.data[y_col], color='skyblue')
        ax.set_title('Sales by Branch')
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.set_xticklabels(self.data[x_col], rotation=20, ha='right')
        ax.grid(True, axis='y')
        #plt.show()

        return fig, recommendation
    def analyze_probar_chart(self, x_col, y_col):
        # Calculate the total and proportional sales
        total_sales = self.data[y_col].sum()
        proportional_sales = self.data[y_col] / total_sales
        
        # Identify branches with extreme values
        highest_sales_branch = self.data.loc[self.data[y_col].idxmax(), x_col]
        lowest_sales_branch = self.data.loc[self.data[y_col].idxmin(), x_col]
        
        recommendation = (
            f"Branch {highest_sales_branch} has the highest sales. "
            f"Consider increasing distribution here.\n"
            f"Branch {lowest_sales_branch} has the lowest sales. "
            f"Consider reducing distribution or investigating potential issues."
        )
        
        # Plot the bar chart
        fig, ax = plt.subplots(figsize=(6, 7))
        ax.bar(self.data[x_col], self.data[y_col], color='skyblue')
        ax.set_title('Product Sales by Branch')
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.set_xticklabels(self.data[x_col], rotation=20, ha='right')
        ax.grid(True, axis='y')
        #plt.show()

        return fig, recommendation
            
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
    welcome = ADboard()
    window = QStackedWidget()
    window.addWidget(welcome) 
    window.setWindowTitle("My logistics App")
    window.resize(int(width), int(height))
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()