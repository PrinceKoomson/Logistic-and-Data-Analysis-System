import sys
from PyQt5.uic import loadUi
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QMessageBox
from PyQt5.QtGui import QIcon

import mysql.connector as con
def Db(query):
    db = con.connect(host = "localhost", user = "root", password = "MySql", database = "emp")
    cursor = db.cursor()
    cursor.execute(query)
    result = cursor.fetchone()
    return result

#Homepage
class Homepage(QDialog):
    def __init__(self):
        super(Homepage, self).__init__()
        loadUi("Homepage.ui", self)
        #Buttons 
        self.AdminButton.clicked.connect(self.adminpage)
        self.UserButton.clicked.connect(self.userpage)

    def adminpage(self):
        Adpage = AdminloginPage()
        widget.addWidget(Adpage)
        widget.setCurrentIndex(widget.currentIndex()+ 1)
    
    def userpage(self):
        Upage = UserloginPage()
        widget.addWidget(Upage)
        widget.setCurrentIndex(widget.currentIndex()+ 1)

#Admin login page
class AdminloginPage(QDialog):
    def __init__(self):
        super(AdminloginPage, self).__init__()
        loadUi("AdminloginPage.ui", self)
        self.PassBox.setEchoMode(QtWidgets.QLineEdit.Password)
        self.BackLink.clicked.connect(self.home)
        self.AloginButton.clicked.connect(self.adminlogin)
    def home(self):
        homepage = Homepage()
        widget.addWidget(homepage)
        widget.setCurrentIndex(widget.currentIndex()+1)
