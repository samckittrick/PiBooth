# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1368, 768)
        self.centralWidget = QtWidgets.QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")
        self.stackedWidget = QtWidgets.QStackedWidget(self.centralWidget)
        self.stackedWidget.setGeometry(QtCore.QRect(0, 0, 1368, 768))
        self.stackedWidget.setObjectName("stackedWidget")
        self.page = QtWidgets.QWidget()
        self.page.setObjectName("page")
        self.gridLayoutWidget = QtWidgets.QWidget(self.page)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(0, 0, 1371, 771))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(11, 11, 11, 11)
        self.gridLayout.setSpacing(6)
        self.gridLayout.setObjectName("gridLayout")
        self.NameLabel = QtWidgets.QLabel(self.gridLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(20)
        self.NameLabel.setFont(font)
        self.NameLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.NameLabel.setObjectName("NameLabel")
        self.gridLayout.addWidget(self.NameLabel, 0, 0, 1, 1)
        self.stackedWidget.addWidget(self.page)
        self.page_2 = QtWidgets.QWidget()
        self.page_2.setObjectName("page_2")
        self.gridLayoutWidget_2 = QtWidgets.QWidget(self.page_2)
        self.gridLayoutWidget_2.setGeometry(QtCore.QRect(70, 110, 1221, 611))
        self.gridLayoutWidget_2.setObjectName("gridLayoutWidget_2")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.gridLayoutWidget_2)
        self.gridLayout_2.setContentsMargins(11, 11, 11, 11)
        self.gridLayout_2.setSpacing(6)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.templateView = QtWidgets.QListView(self.gridLayoutWidget_2)
        self.templateView.setObjectName("templateView")
        self.gridLayout_2.addWidget(self.templateView, 0, 0, 1, 1)
        self.label = QtWidgets.QLabel(self.page_2)
        self.label.setGeometry(QtCore.QRect(480, 40, 431, 41))
        font = QtGui.QFont()
        font.setPointSize(27)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.stackedWidget.addWidget(self.page_2)
        self.page_3 = QtWidgets.QWidget()
        self.page_3.setObjectName("page_3")
        self.label_3 = QtWidgets.QLabel(self.page_3)
        self.label_3.setGeometry(QtCore.QRect(480, 30, 331, 41))
        font = QtGui.QFont()
        font.setPointSize(27)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.resultImageLabel = QtWidgets.QLabel(self.page_3)
        self.resultImageLabel.setGeometry(QtCore.QRect(250, 110, 871, 511))
        self.resultImageLabel.setText("")
        self.resultImageLabel.setScaledContents(True)
        self.resultImageLabel.setObjectName("resultImageLabel")
        self.stackedWidget.addWidget(self.page_3)
        MainWindow.setCentralWidget(self.centralWidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.NameLabel.setText(_translate("MainWindow", "Qt-Py PhotoBooth"))
        self.label.setText(_translate("MainWindow", "Please Select a Template"))
        self.label_3.setText(_translate("MainWindow", "Your Photo is Ready!"))

