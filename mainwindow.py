"""
Module representing the GUI to be shown on screen.
By: Scott McKittrick

Dependencies:

Classes Contained:

"""

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

##################################################################
# MainGuiWindow
##################################################################
class MainGuiWindow:
    """ Class for the main gui window. """

    #-----------------------------------------------------------#
    def __init__(self, screenWidth, screenHeight, lf):
        self.logoFile = lf
        self.screenWidth = screenWidth
        self.screenHeight = screenHeight
        
    #------------------------------------------------------------#
    def getSplashScreen(self):
        #Set up the splash screen page
        self.splashPage = QtWidgets.QWidget()
        self.splashPage.setObjectName("splashPage")
        self.splash_gridLayout = QGridLayout(self.splashPage)
        self.logoLabel = QLabel()
        self.pixmap = QPixmap(self.logoFile)
        #calculate scale factors
        vertScale = (self.screenWidth/2)/self.pixmap.size().width()
        print("VertScale: " + str(vertScale))
        horizScale = (self.screenHeight/2)/self.pixmap.size().height()
        print("HorizScale: " + str(horizScale))
        #whichever axis has the greatest change in size (i.e. is the smallest percentage of the original size) is the scale factor.
        if(vertScale < horizScale):
            self.pixmap = self.pixmap.scaledToHeight(self.pixmap.size().height() * vertScale, QtCore.Qt.SmoothTransformation)
        else:
            self.pixmap = self.pixmap.scaledToWidth(self.pixmap.size().width() * horizScale, QtCore.Qt.SmoothTransformation)
        self.logoLabel.setPixmap(self.pixmap)
        self.logoLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.splash_gridLayout.addWidget(self.logoLabel, 0,0,1,1)
        return self.splashPage
                                                                                                                                                    
    #-----------------------------------------------------------#
    def initUI(self):
        """Initialize the UI Window. """


        #Configure the main window
        self.mainWindow = QMainWindow()
        self.mainWindow.showFullScreen()
        
        self.mainWindow.setObjectName("MainWindow")
        self.mainWindow.resize(self.screenWidth, self.screenHeight)

        #Set up the stacked widget. This provides a way to load all the pages
        # at the beginning and just switch them when we need them. 
        self.stackedWidget = QtWidgets.QStackedWidget(self.mainWindow)
        self.stackedWidget.setGeometry(QtCore.QRect(0, 0, self.screenWidth, self.screenHeight))
        #self.stackedWidget.setLayout(QtCore.Qt.LeftToRight) 
        self.stackedWidget.setObjectName("stackedWidget")

        #Add the splash screen
        self.stackedWidget.addWidget(self.getSplashScreen())

        #add the stacked widget to the window
        self.mainWindow.setCentralWidget(self.stackedWidget)


        
    #-----------------------------------------------------------#
    def showMainWindow(self):
        self.mainWindow.show()
        
        
