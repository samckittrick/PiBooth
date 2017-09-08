"""Qt & Python Based Photo Booth
By: Scott McKittrick

Features:
Configurable and selectable templates

Dependencies:
PyQt5

Classes Contained:
QtPyPhotobooth - Main Application controller class.

"""
from enum import Enum
import time
import os

import PyQt5
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer,QObject, QSize
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QPixmap, QIcon

import mainwindow_auto
from PhotoboothCamera import PhotoboothCamera
from PhotoboothConfig import PhotoboothConfig
from PhotoboothTemplate import TemplateManager

################################################################
# QtPyPhotobooth Class                                         #
################################################################
class QtPyPhotobooth(QObject):
    """Main application class. Initializes and controls the application """

    ##############################
    #Screen List                 #
    ##############################
    class Screens(Enum):
        SPLASH = 0
        TEMPLATE = 1

    #-----------------------------------------------------------#    
    def __init__(self):
        """QtPyPhotobooth constructor. 
        Takes no Arguments."""

        #initialise some paths
        self.resourcePath = "." + os.path.sep + "res"
        self.defaultTemplateIcon = "defaultTemplateIcon.png"
        
        print("Initializing configuration...")
        self.config = PhotoboothConfig()

        print("Intializing  Gui...")
        self.form = mainwindow_auto.Ui_MainWindow()
        self.mainWindow = QMainWindow()
        self.form.setupUi(self.mainWindow)

        #Start pulling references to important widgets
        self.stackedWidget = self.form.stackedWidget
        self.templateView = self.form.templateView

        #Configure the main window
        self.mainWindow.showFullScreen()
        screenSize = self.mainWindow.size()
        print("Screen size: ")
        print("\tWidth: " + str(screenSize.width()))
        print("\tHeight: " + str(screenSize.height()))

        #Configure the camera
        print("Initializing camera hardware")
        self.camera = PhotoboothCamera()

        #Configure the template list.
        print("Initializing Templates...")
        self.templateManager = TemplateManager(self.config.getTemplateLocation())
        self.__configureTemplateView()

        self.mainWindow.show()

        #Show the splash screen for a specific amount of time before moving on.
        self.timer = QTimer()
        self.timer.setInterval(self.config.getSplashScreenTime())
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(lambda : self.__changeScreens(QtPyPhotobooth.Screens.TEMPLATE))
        self.timer.start()
        


    #-----------------------------------------------------------#
    def __changeScreens(self, screen):
        """Changes the screens on the gui to the selected screen"""
        self.stackedWidget.setCurrentIndex(screen.value)

    #-----------------------------------------------------------#
    def __configureTemplateView(self):
        """Read the list of template items and add them to the screen."""
        #Configure icon mode
        #configure size
        #create templateListModel class
        #create templatDelegate class
        self.templateModel = QStandardItemModel()
        for template in self.templateManager:
            item = QStandardItem()
            item.setText(template.templateName)
            previewPath = template.getTemplatePreviewPath()
            if(previewPath != None):
                pixmap = QPixmap(previewPath)
            else:
                pixmap = QPixmap(self.resourcePath + os.path.sep + self.defaultTemplateIcon)
            item.setIcon(QIcon(pixmap))
            #ToDo Add some error handling for missing or unspecified preview images. Include res directory for default icons
            self.templateModel.appendRow(item)
        
        self.templateView.setViewMode(QListView.IconMode)
        self.templateView.setIconSize(QSize(150,150))
        self.templateView.setUniformItemSizes(True)
        self.templateView.setSpacing(50)
        self.templateView.setModel(self.templateModel)
    

    
####################################
#Main function
####################################
if(__name__ == '__main__'):
    import sys

    app = QApplication(sys.argv)
    mApplication = QtPyPhotobooth()
    sys.exit(app.exec_())
