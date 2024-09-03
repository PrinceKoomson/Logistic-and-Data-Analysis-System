import sys
import os
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIntValidator, QPixmap
from PyQt5.QtCore import QDateTime, QDate, QTimer, Qt
from PyQt5.QtWidgets import QWidget, QApplication, QDialog, QStackedWidget, QTableWidget,  QAbstractItemView,  QToolButton, QWidget, QComboBox, QHBoxLayout, QVBoxLayout, QTableWidgetItem, QMessageBox
from Employee import EmpDboard
from Admin import ADboard
from Manager import Manboard
import hashlib
#import importlib

#DB connection
import mysql.connector as con
db = con.connect(host="127.0.0.1", user="root", password ="", database ="logisticsdb")
cursor = db.cursor()

class Loginpage(QDialog):
    branch = ""
    SalePerson = ""
    def __init__(self):
        super(Loginpage, self).__init__()
        main_dir = os.path.dirname(os.path.abspath(__file__))
        EmpUi = os.path.join(main_dir, 'Ui', 'Loginpage.ui')
        loadUi(EmpUi, self)
        self.PwordBox.setEchoMode(QtWidgets.QLineEdit.Password)
        self.LoginButton.clicked.connect(self.Ulogin)


    def Ulogin(self):
        Uname = self.UnameBox.text()
        Pword = self.PwordBox.text()
        PwordHashed = hashlib.sha256(Pword.encode('utf-8')).hexdigest()
        
        if len(Uname) == 0 or len(Pword) == 0:
            self.error.setText("Please input all fields.")
            return

        # Check if user is a Salesperson
        query = "SELECT Password, CONCAT(First_name, ' ', Last_name), Branch_name FROM salespersons WHERE Email = %s"
        cursor.execute(query, (Uname,))
        result = cursor.fetchone()
        
        if result:
            stored_password, SalePerson, Branch = result
            if PwordHashed == stored_password:
                dboard = EmpDboard()
                self.saleline = dboard.Uline
                self.brline = dboard.Bline
                dboard.EmpName.setText(SalePerson)
                dboard.BrName.setText(Branch)
                self.saleline.setText(SalePerson)
                self.brline.setText(Branch)
                widget.addWidget(dboard)
                widget.setCurrentIndex(widget.currentIndex() + 1)
                QMessageBox.information(None, "Successful", "You are logged in successfully.")
                return
            else:
                self.PwordBox.clear()
                self.error.setText("Incorrect password!")
                return
        
        # Check if user is a Manager
        query = "SELECT Password, Branch_name FROM managers WHERE Email = %s"
        cursor.execute(query, (Uname,))
        result = cursor.fetchone()
        
        if result:
            stored_password, Branch = result
            if PwordHashed == stored_password:
                dboard = Manboard()
                self.manline = dboard.Brline
                if Branch:
                    self.manline.setText(Branch)
                widget.addWidget(dboard)
                widget.setCurrentIndex(widget.currentIndex() + 1)
                QMessageBox.information(None, "Successful", "You are logged in successfully.")
                return
            else:
                self.PwordBox.clear()
                self.error.setText("Incorrect password!")
                return
        
        # Check if user is an Admin
        query = "SELECT Password FROM Admin WHERE Email = %s"
        cursor.execute(query, (Uname,))
        result = cursor.fetchone()
        
        if result:
            stored_password = result[0]
            if Pword == stored_password:
                dboard = ADboard()
                widget.addWidget(dboard)
                widget.setCurrentIndex(widget.currentIndex() + 1)
                QMessageBox.information(None, "Successful", "You are logged in successfully.")
                return
            else:
                self.PwordBox.clear()
                self.error.setText("Incorrect password!")
                return

        # If no user found
        self.error.setText("User not found!")

    def Ulogin0(self):
        Uname = self.UnameBox.text()
        Pword = self.PwordBox.text()
        PwordHashed = hashlib.sha256(Pword.encode('utf-8')).hexdigest()
        if len(Uname) == 0 or len(Pword) == 0:
            self.error.setText("Please input all fields.")
        else:
            query = "SELECT * FROM salespersons WHERE Email = %s"
            cursor.execute(query, (Uname,))
            result = cursor.fetchone()
            if result:
                query = "SELECT Password FROM salespersons WHERE Email = %s"
                cursor.execute(query, (Uname,))
                result = cursor.fetchone()
                if PwordHashed == result[0]:
                    dboard = EmpDboard()
                    #Get Branch and salesPerson serving
                    SalePque = "SELECT CONCAT(First_name, ' ', Last_name) FROM salespersons WHERE Email=%s"
                    cursor.execute(SalePque, (Uname,))
                    FName = cursor.fetchone()

                    brque = "SELECT Branch_name FROM salespersons WHERE Email = %s"
                    cursor.execute(brque, (Uname,))
                    Branch = cursor.fetchone()

                    SalePerson = f"{FName[0]}"# {LName[0]}"
                    branch = Branch[0]
                    self.saleline = dboard.Uline
                    self.brline = dboard.Bline
                    dboard.EmpName.setText(SalePerson)
                    dboard.BrName.setText(branch)

                    self.saleline.setText(SalePerson)
                    self.brline.setText(Branch[0])

                    widget.addWidget(dboard)
                    widget.setCurrentIndex(widget.currentIndex()+1)
                    QMessageBox.information(None, "Successful", "You are logged successfully.")
                    
                else:
                    self.PwordBox.clear()
                    self.error.setText("Incorrect password!")
            elif not result:
                query = "SELECT * FROM Managers WHERE Email = %s"
                cursor.execute(query, (Uname,))
                result = cursor.fetchone()
                if result:
                    query = "SELECT Password FROM Managers WHERE Email = %s"
                    cursor.execute(query, (Uname,))
                    result = cursor.fetchone()
                    if PwordHashed == result[0]:
                        dboard = Manboard()
                        #Get Branch
                        brque = "SELECT Branch_name FROM salespersons WHERE Email = %s"
                        cursor.execute(brque, (Uname,))
                        Branch = cursor.fetchone()
                        if Branch:
                            self.manline = dboard.Brline
                            self.manline.setText(Branch[0])

                        widget.addWidget(dboard)
                        widget.setCurrentIndex(widget.currentIndex()+1)
                        QMessageBox.information(None, "Successful", "You are logged successfully.")
                        
                    else:
                        self.PwordBox.clear()
                        self.error.setText("Incorrect password!")
                elif not result:
                    query = "SELECT * FROM Admin WHERE Email = %s"
                    cursor.execute(query, (Uname,))
                    result = cursor.fetchone()
                    if result:
                        query = "SELECT Password FROM Admin WHERE Email = %s"
                        cursor.execute(query, (Uname,))
                        result = cursor.fetchone()
                        if Pword == result[0]:
                            dboard = ADboard()
                            widget.addWidget(dboard)
                            widget.setCurrentIndex(widget.currentIndex()+1)
                            QMessageBox.information(None, "Successful", "You are logged successfully.")
                            #dboard.Uline.setText(Uname)
                    else:
                        self.error.setText("User not found!")
    

import ctypes
def screendim():
    user32 = ctypes.windll.user32
    width = user32.GetSystemMetrics(0)
    height = user32.GetSystemMetrics(1)
    return width, height
width, height = screendim()

app = QApplication(sys.argv)
welcome = Loginpage()
widget = QStackedWidget()
widget.addWidget(welcome) 
widget.setWindowTitle("My logistics App")
widget.resize(int(width), int(height))
widget.show()
sys.exit(app.exec())