import sys
import os
import datetime
import math
import secrets
import string
import hashlib
import time
import threading
import re
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PyQt5 import QtWidgets, QtGui
from PyQt5.uic import loadUi
from PyQt5.QtCore import QDate, Qt, QDateTime, QTimer, QRect, QSize, QPropertyAnimation, QPoint
from PyQt5.QtWidgets import (
    QApplication, QDialog, QStackedWidget, QMessageBox, QTableWidgetItem, QAbstractItemView,
    QFileDialog, QLineEdit, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QButtonGroup, QListView, QStyledItemDelegate, QWidget, QToolButton, QPushButton, QSizePolicy, QListWidgetItem, QTableWidget, QListWidget,
)
from PyQt5.QtGui import (
    QDoubleValidator, QIntValidator, QColor, QFont, QFontMetrics, QPainter,
    QStandardItem, QStandardItemModel, QPixmap, QPolygon, 
)  
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

#database connection
import mysql.connector as con
db = con.connect(host="127.0.0.1", user="root", password ="", database ="logisticsdb")
cursor = db.cursor()

# Initialize the cache
class Manboard(QDialog):
    def __init__(self):
        super(Manboard, self).__init__()
        main_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(main_dir, 'Ui', 'Manager.ui')
        loadUi(ui_path, self)
        self.Brline = QLineEdit()
        self.Brline.hide()
        self.InvTable.hide()
        self.EmployeeTable.hide()
        self.ReportTable.hide()
        self.MessageArea.hide()
        self.homewid.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.homewid.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.branch_name = self.Brline.text()
        self.senderName = "Branch manager"
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
        # Create menu buttons and set their object names
        buttons = ["Inventory", "Employees", "Report", "LogOut"]
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
        button_names = ["Inventorybtn", "Employeesbtn", "Reportbtn", "LogOutbtn"]
        for name in button_names:
            btn = self.findChild(QToolButton, name)
            if btn:
                btn.setStyleSheet(toolbcss)
                btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Apply hover effect after the widget is fully shown
        self.init_hover_effects()
        self.refresh_inventory()
        self.homepage()
        self.MessageButton.clicked.connect(self.Messages)
 
    def Report(self):
        print(self.branch_name)
        self.homewid.clear()
        self.ButtonList.clear()

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
                widget_item.setStyleSheet("")  # Reset style for other items

        branch = self.senderName
        
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
        report_ai = ReportAI(tsdf)
        TSalesgraph, sales_summary = report_ai.analyze_line_chart('date', 'sales')

        report_ai = ReportAI(prdf)
        bargraph, product_summary = report_ai.analyze_bar_chart('Product_name', 'Total_Quantity')

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
    def SalesDet(self):
        saleslinequery = "SELECT DATE(Sale_Date) AS day, SUM(Quantity) AS total_quantity FROM sales GROUP BY DATE(Sale_Date) ORDER BY DATE(Sale_Date)"
        cursor.execute(saleslinequery)
        tsresult = cursor.fetchall()
        tsdf = pd.DataFrame(tsresult, columns=['date', 'sales'])
        
        report_ai = ReportAI(tsdf)
        TSalesgraph, sales_summary = report_ai.analyze_line_chart('date', 'sales')  # Correctly call the method
        plt.show()
        self.Report()
        

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

    def Inventory(self):
        # Clear existing content
        self.homewid.clear()
        self.ButtonList.clear()
        self.homepage()
        #self.home.show()
        menustyle_selected = '''
                QWidget {
                    background-color: #1abc9c;  /* Teal color for selected item */
                    color: white;
                }

                QToolButton {
                    color: white;
                }
            '''
        # Apply the selected style to the Inventory button's container
        for i in range(self.MenuList.count()):
            widget_item = self.MenuList.itemWidget(self.MenuList.item(i))
            btn = widget_item.findChild(QToolButton)
            if btn and btn.text() == "Inventory":
                widget_item.setStyleSheet(menustyle_selected)
            else:
                widget_item.setStyleSheet("")  # Reset style for other items

        #self.MenuList.setStyleSheet(menustyle)
        self.MessageArea.hide()
      
    def homepage(self):
        # Query data
        #self.refresh_inventory()
        query = "SELECT DATE(Sale_Date) AS day, SUM(Quantity) AS total_quantity FROM sales WHERE Branch_name = 'Computech' GROUP BY DATE(Sale_Date) ORDER BY DATE(Sale_Date)"
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
        
        # Apply the layout to the main window
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
        self.stockCount = QLabel("950")
        self.stock.setAlignment(Qt.AlignCenter)
        self.stockCount.setAlignment(Qt.AlignCenter)
        
        self.stock.setStyleSheet("color: green; font-size: 24px; font-weight: bold;")
        self.stockCount.setStyleSheet("color: green; font-size: 48px; font-weight: bold;")
        
        # Create QVBoxLayout and add widgets
        slayout = QVBoxLayout()
        slayout.addWidget(self.stock)
        slayout.addWidget(self.stockCount)
        StockBox = QWidget()
        
        slayout.setAlignment(Qt.AlignCenter)
        StockBox.setFixedWidth(150)
        StockBox.setLayout(slayout)
        StockBox.setStyleSheet(sheet)

        canvas = self.reporting.line_chart(sales_data, "date", "sales", title='', x_label='', y_label='')
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

        font = QFont('Palatino Linotype 23')
        ttt = self.duplicate_table(self.InvTable)
        
        #tt.setStyleSheet(tablesheet)
        ttt.setFont(font)
        ttt.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        ttt.verticalHeader().setVisible(False)
        #ttt.setStyleSheet("border-left: 1px solid")
        ttt.setColumnWidth(0, 450)
        layout = QHBoxLayout()
        layout.addWidget(ttt)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(50, 50, 50, 50)
        inv = QWidget()
        inv.setLayout(layout)
        hei = self.InvTable.height()


        table_item = QListWidgetItem()
        #table_item.setSizeHint(QSize(layout.sizeHint()))
        table_item.setSizeHint(QSize(100, hei))

        
        self.homewid.addItem(table_item)
        self.homewid.setItemWidget(table_item, inv)
        
    def refresh_inventory(self):
        self.InvTable.setColumnWidth(0, 245)
        self.InvTable.setColumnWidth(1, 125)
        self.InvTable.setColumnWidth(2, 125)
        self.InvTable.setColumnWidth(3, 125)

        try:
            # Fetch product details
            spquery = "SELECT Spec_ID, Product_name FROM specificproducts"
            cursor.execute(spquery)
            prods = cursor.fetchall()

            branch = "Computech"
            self.InvTable.setRowCount(len(prods))

            for row, (spec_id, product_name) in enumerate(prods):
                pro = f"{spec_id} - {product_name}"
                self.InvTable.setItem(row, 0, QTableWidgetItem(pro))

                # Fetch quantity sold
                soldquery = "SELECT SUM(Quantity) FROM sales WHERE Spec_ID = %s AND Branch_name = %s"
                cursor.execute(soldquery, (spec_id, branch))
                qty = cursor.fetchone()[0]
                sold = int(qty) if qty is not None else 0
                self.InvTable.setItem(row, 2, QTableWidgetItem(str(sold)))

                # Fetch quantity in stock
                instockquery = f"SELECT {branch} FROM inventory WHERE Spec_ID = %s"
                cursor.execute(instockquery, (spec_id,))
                result = cursor.fetchone()
                instock = str(result[0]) if result else '0'
                self.InvTable.setItem(row, 1, QTableWidgetItem(instock))
                pricequery = "SELECT Price FROM specificproducts WHERE Spec_ID= %s"
                cursor.execute(pricequery, (spec_id,))
                price = cursor.fetchone()[0]
                self.InvTable.setItem(row, 3, QTableWidgetItem(str(price)))
            #self.InvTable.set
            

        except con.Error as err:
            # Display error message if an exception occurs
            QMessageBox.critical(self, "Database Error", f"An error occurred: {err}")

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
                widget_item.setStyleSheet("")  # Reset style for other items
        
        ttt = self.duplicate_table(self.EmployeeTable)
        ttt.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        ttt.verticalHeader().setVisible(False)
        layout = QHBoxLayout()
        layout.addWidget(ttt)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(50, 50, 50, 50)
        inv = QWidget()
        inv.setLayout(layout)
        hei = self.InvTable.height()
        table_item = QListWidgetItem()
        #table_item.setSizeHint(QSize(layout.sizeHint()))
        table_item.setSizeHint(QSize(100, hei))
        self.homewid.addItem(table_item)
        self.homewid.setItemWidget(table_item, inv)

    
        self.MessageArea.hide()

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
        # Create menu buttons and set their object names
        buttons = ["Add", "Edit", "Delete"]
        for btn_name in buttons:
            btn = QToolButton()
            btn.setText(btn_name)
            btn.setObjectName(f"{btn_name}btn")
            btn.setStyleSheet(toolbcss)
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
    def Add(self):
        form = AddEmployee(self)
        form.exec()
        self.EmRefresh()
    def Edit(self):
        form = EditEmployee()
        form.exec()
        self.EmRefresh()
    def Delete(self):
        form = DelEmployee(self)
        form.exec()
    def EmRefresh(self):
        self.EmployeeTable.setColumnWidth(0, 150)
        self.EmployeeTable.setColumnWidth(1, 270)
        self.EmployeeTable.setColumnWidth(2, 150)
        self.EmployeeTable.setColumnWidth(3, 250)
        try:
            query = "SELECT ID, CONCAT(First_name, ' ', Last_name) AS FullName, Phone, Email FROM salespersons"
            cursor.execute(query)
            result = cursor.fetchall()
            self.EmployeeTable.setRowCount(len(result))

            for row_num, row_data in enumerate(result):
                for col_num, data in enumerate(row_data):
                    self.EmployeeTable.setItem(row_num, col_num, QTableWidgetItem(str(data)))

        except con.Error as err:
            QMessageBox.critical(self, "Database Error", f"An error occurred: {err}")

    def LogOut(self):
        Confirm = QMessageBox.information(None, "Warning", "Are you sure you want to logout and exit", QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)
        if Confirm == QMessageBox.Ok:
            sys.exit()

    def duplicate_table(self, original_table):
        new_table = QTableWidget()
        new_table.setRowCount(original_table.rowCount())
        new_table.setColumnCount(original_table.columnCount())

        new_table.setHorizontalHeaderLabels(
            [original_table.horizontalHeaderItem(i).text() for i in range(original_table.columnCount())]
        )

        new_table.setVerticalHeaderLabels(
            [
                original_table.verticalHeaderItem(i).text() if original_table.verticalHeaderItem(i) else ""
                for i in range(original_table.rowCount())
            ]
        )

        for row in range(original_table.rowCount()):
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
         # Apply borders by selecting the entire table and setting a border style
        for row in range(new_table.rowCount()):
            for column in range(new_table.columnCount()):
                new_table.item(row, column).setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                new_table.item(row, column).setTextAlignment(Qt.AlignCenter)
        # Copy column widths
        for col in range(original_table.columnCount()):
            new_table.setColumnWidth(col, original_table.columnWidth(col))

        # Copy row heights
        for row in range(original_table.rowCount()):
            new_table.setRowHeight(row, original_table.rowHeight(row))
        new_table.setStyleSheet("""
                /* General Table Styles */
                QTableWidget {
                    gridline-color: #D6DBDF; /* Light grey grid lines */
                    background-color: #FFFFFF; /* White background */
                    alternate-background-color: #F7F9F9; /* Light grey for alternate rows */
                    font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif; /* Modern font */
                    font-size: 12pt; /* Font size */
                    border: 1px solid #D6DBDF; /* Light grey border around the table */
                }

                /* Header Styles */
                QHeaderView::section {
                    background-color: #2C3E50; /* Dark blue-grey background for header */
                    color: white; /* White text color for header */
                    font-weight: bold; /* Bold text in headers */
                    padding: 6px; /* Padding around header text */
                    border: 1px solid #D6DBDF; /* Light grey border */
                    border-bottom: 2px solid #2980B9; /* Thicker bottom border */
                    text-align: center; /* Center-align the text in headers */
                }

                /* Cell Styles */
                QTableWidget::item {
                    border-bottom: 1px solid #D6DBDF; /* Light grey bottom border for cells */
                    padding: 6px; /* Padding around cell content */
                    text-align: center; /* Center-align the text in cells */
                }
                
                /* Alternating Row Colors */
                QTableWidget::item:alternate {
                    background-color: #F7F9F9; /* Light grey for alternate rows */
                }

                /* Selected Cell Styles */
                QTableWidget::item:selected {
                    background-color: #85C1E9; /* Light blue background for selected cells */
                    color: #FFFFFF; /* White text for selected cells */
                }

                /* First Column Left Border */
                QTableWidget::item {
                    border-left: 1px solid #D6DBDF; /* Light grey left border for each cell */
                }

                /* Scrollbar Styles */
                QScrollBar:vertical {
                    background: #F0F3F4; /* Light background for scrollbar */
                    width: 12px; /* Width of scrollbar */
                    margin: 18px 0 18px 0; /* Margins to match the table */
                    border: 1px solid #D6DBDF; /* Light grey border */
                }
                QScrollBar::handle:vertical {
                    background: #BDC3C7; /* Grey handle */
                    min-height: 20px; /* Minimum height of handle */
                    border-radius: 6px; /* Rounded corners for handle */
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    border: none; /* Remove arrows */
                    background: none; /* No background for arrows */
                }
            """)
        new_table.setSelectionMode(QListWidget.NoSelection)
        return new_table

    def init_message_display(self):
        # Set item delegate for custom message display
        delegate = MessageDelegate()
        self.MessageDisp.setItemDelegate(delegate)

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


    #Animations
    def init_hover_effects(self):
        QTimer.singleShot(0, self.apply_hover_effects)
    def apply_hover_effects(self):

        button_names = ["Inventorybtn", "Employeesbtn", "Reportbtn", "LogOutbtn"]

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

        self.Managername = QLineEdit()
        self.Managername.setVisible(False)
        


        branch = self.Managername.text()
        gender_group = QButtonGroup(self)
        gender_group.addButton(self.MaleCheck)
        gender_group.addButton(self.FemaleCheck)
        gender_group.setExclusive(True)
        self.Poswidget.hide()
        self.Gender=""
        self.getGen()
        self.StoCombo.addItem(branch)
    def getGen(self):
        if self.MaleCheck.isChecked():
            self.Gender = "M"
        if self.FemaleCheck.isChecked():
            self.Gender = "F"

    def AddEmp(self):
        FName = self.Fname.text()
        LName = self.Lname.text()
        Email = self.Email.text()
        Phone = self.Phone.text()
        self.position = "Salesperson"
        self.getGen()

        #Branch = self.StoCombo.currentText()
        self.Branch = "FlexTech"
        date = self.AddDate.date()
        self.Date = date.toString("yyyy-MM-DD")

        if len(FName) == 0 or len(LName) == 0 or len(Email) == 0 or len(Phone) == 0 or self.Gender == "":
            self.Error.setText("Please input all fields!")
        else:
            if len(Phone) != 10:
                self.Error.setText("Invalid phone number!")
            else:
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
                    query = "INSERT INTO salespersons (First_name, Last_name, Email, Phone, Branch_Name, Position, Date_of_birth, Gender, Password) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    values = (FName, LName, Email, Phone, self.Branch, self.position, self.Date, self.Gender, hashed_password)
                    cursor.execute(query, values)
                    db.commit()

                QMessageBox.information(None, "Success", f"Employee added successfully.\nGenerated Password: {Pword}")
                self.Closeform()                   
    def Closeform(self):
        self.close()

class DelEmployee(QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        main_dir = os.path.dirname(os.path.abspath(__file__))
        Ui = os.path.join(main_dir, 'Ui', 'DelEmp.ui')
        loadUi(Ui, self)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.Confirm.clicked.connect(self.DelEmp)
        self.Cancel.clicked.connect(self.Closeform)
        self.Close.clicked.connect(self.Closeform)

    def DelEmp(self):
        Name = self.Name.text()#.replace(" ", "_")
        Branch = self.Branch.text()
        if len(Name) == 0 or len(Branch) == 0:
            self.Error.setText("Please input all fields!")
        else:
            query = "select * from Employee where Employee_Name = '"+Name+"'"
            cursor.execute(query)
            result = cursor.fetchone()
            if result:
                query = ("delete from Employee where Employee_Name ='"+Name+"'")
                cursor.execute(query)
                db.commit()
                #Update credential
                query2 = "DELETE FROM credentials WHERE Employee_Name = '"+Name+"'"
                cursor.execute(query2)
                db.commit()
                QMessageBox.information(None, "Success", "Employee removed successfully")
                self.Closeform()    
            else:
                QMessageBox.warning(None, "Warning", "User does not exist.")
        
    def Closeform(self):
        self.close()

class Message(object):
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
        font = QFont("Helvetica", 10)  # WhatsApp uses a clean sans-serif font
        painter.setFont(font)

        # Define the padding, bubble color, and text color
        padding = 15
        bubble_color = QColor(225, 255, 199) if message.is_received else QColor(220, 248, 198)
        text_color = QColor(0, 0, 0) if message.is_received else QColor(0, 0, 0)

        # Calculate the text rectangle size
        text_rect = painter.boundingRect(option.rect, Qt.AlignLeft | Qt.AlignVCenter, message.text)
        text_rect = text_rect.adjusted(-padding, -padding, padding, padding)

        # Calculate the bubble rectangle size
        if message.is_received:
            bubble_rect = QRect(option.rect.left() + 15,  # Align left for received messages
                                option.rect.top() + 5,
                                text_rect.width() + 30,
                                text_rect.height() + 20)
        else:
            bubble_rect = QRect(option.rect.right() - text_rect.width() - 45,  # Align right for sent messages
                                option.rect.top() + 5,
                                text_rect.width() + 30,
                                text_rect.height() + 20)

        # Draw the bubble background
        painter.setBrush(bubble_color)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(bubble_rect, 15, 15)

        # Draw the message text inside the bubble
        painter.setPen(text_color)
        painter.drawText(bubble_rect.adjusted(padding - 10, padding - 5, -padding + 10, -padding + 5),
                        Qt.AlignLeft | Qt.AlignVCenter,
                        message.text)



    '''def paint(self, painter, option, index):
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
            bubble_rect = QRect(option.rect.left() + 10,  # Align left for received messages
                                option.rect.top() + 10,
                                text_rect.width() + 20,
                                text_rect.height() + 10)
        else:
            bubble_rect = QRect(option.rect.right() - text_rect.width() - 30,  # Align right for sent messages
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
                         message.text)'''

    def sizeHint(self, option, index):
        # Adjust size hint based on message length
        model = index.model()
        message = model.data(index, Qt.UserRole)
        text_rect = QFontMetrics(option.font).boundingRect(0, 0, option.rect.width() - 40, 0, Qt.TextWordWrap, message.text)
        return QSize(option.rect.width(), text_rect.height() + 30)

class ManReporting:
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


class ReportAI:
    def __init__(self, data):
        self.data = data

    def analyze_line_chart(self, x_col, y_col):
        # Calculate the trend using the rolling average
        rolling_mean = self.data[y_col].rolling(window=5).mean()

        # Generate a summary focused on progress or decline
        if rolling_mean.iloc[-1] > rolling_mean.iloc[0]:
            summary = "The line chart indicates progress, with sales improving over the analyzed period."
        elif rolling_mean.iloc[-1] < rolling_mean.iloc[0]:
            summary = "The line chart indicates a decline, with sales decreasing over the analyzed period."
        else:
            summary = "The line chart indicates stability, with no significant change in sales over the analyzed period."

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

        return fig, summary

    def analyze_bar_chart(self, x_col, y_col):
        # Calculate total sales
        total_sales = self.data[y_col].sum()

        # Identify branches with extreme values
        highest_sales_branch = self.data.loc[self.data[y_col].idxmax(), x_col]
        lowest_sales_branch = self.data.loc[self.data[y_col].idxmin(), x_col]

        # Generate a summary focused on progress or decline in distribution
        if self.data[y_col].max() > self.data[y_col].mean():
            summary = (
                f"The bar chart indicates progress for Branch {highest_sales_branch}, "
                f"which has significantly higher sales compared to others."
            )
        else:
            summary = (
                f"The bar chart indicates a decline in performance for Branch {lowest_sales_branch}, "
                f"which has the lowest sales among all branches."
            )

        # Plot the bar chart
        fig, ax = plt.subplots(figsize=(6, 7))
        ax.bar(self.data[x_col], self.data[y_col], color='skyblue')
        ax.set_title('Product Sales')
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.set_xticklabels(self.data[x_col], rotation=20, ha='right', fontsize = 9)
        ax.grid(True, axis='y')
        
        #plt.show()

        return fig, summary

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
    welcome = Manboard()
    window = QStackedWidget()
    window.addWidget(welcome) 
    window.setWindowTitle("My logistics App")
    window.resize(int(width), int(height))
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()