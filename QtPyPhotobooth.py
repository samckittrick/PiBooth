"""Qt & Python Based Photo Booth
By: Scott McKittrick

Features:
Configurable and selectable templates

Dependencies:
PyQt5
PyYAML

Classes Contained:
QtPyPhotobooth - Main Application controller class.

"""
from enum import Enum
import time
import os
import threading

import yaml

from PIL import ImageQt

import PyQt5
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer,QObject, QSize, Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QPixmap, QIcon, QImage

import mainwindow_auto
from PhotoboothCamera import PhotoboothCameraPi, BasicCountdownOverlayFactory
from PhotoboothTemplate import TemplateManager, ImageProcessor
from PhotoboothDelivery import LocalPhotoStorage

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
        PREVIEW = 2
        RESULT = 3
        SAVING = 4
        SAVED = 5
        CONFIGURATION = 6

    #-----------------------------------------------------------#    
    def __init__(self):
        """QtPyPhotobooth constructor. 
        Takes no Arguments."""

        super(QtPyPhotobooth, self).__init__()

        #initialise some members
        self.resourcePath = "." + os.path.sep + "res"
        self.defaultTemplateIcon = "defaultTemplateIcon.png"
        self.templateModel = None
        
        print("Initializing configuration...")
        self.configFilename = "config.yaml"
        f = open(self.configFilename, 'r')
        self.config = yaml.load(f)
        
        print("Intializing  Gui...")
        self.form = mainwindow_auto.Ui_MainWindow()
        self.mainWindow = QMainWindow()
        self.form.setupUi(self.mainWindow)

        #Start pulling references to important widgets
        self.templateLabel = self.form.templateSelectLabel
        self.stackedWidget = self.form.stackedWidget
        self.templateView = self.form.templateView
        self.resultLabel = self.form.resultImageLabel
        self.saveButton = self.form.SaveButton
        self.cancelButton = self.form.CancelButton

        #configure some buttons
        self.cancelButton.clicked.connect(lambda: self.onCancelButtonClicked())
        self.saveButton.clicked.connect(lambda: self.onSaveButtonClicked())

        #Configure the main window
        self.mainWindow.showFullScreen()
        self.screenSize = self.mainWindow.size()
        print("Screen size: ")
        print("\tWidth: " + str(self.screenSize.width()))
        print("\tHeight: " + str(self.screenSize.height()))

        #Configure the camera
        self.__configureCamera()

        #Configure overlays
        self.__configureOverlays()
                
        #Configure the template list.
        self.__configureTemplates()
        self.__configureTemplateView()

        #configure delivery mechanisms
        self.__configureDelivery()

        
        self.__changeScreens(QtPyPhotobooth.Screens.SPLASH)
        self.mainWindow.show()

        #Show the splash screen for a specific amount of time before moving on.
        if('splashScreenTime' in self.config):
            self.splashTime = self.config['splashScreenTime']
        else:
            print("No Splash Screen Time specified. Defaulting to 5 seconds")
            self.splashTime = 5000
        self.timer = QTimer()
        self.timer.setInterval(self.splashTime)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(lambda : self.__changeScreens(QtPyPhotobooth.Screens.TEMPLATE))
        self.timer.start()

    #-----------------------------------------------------------#
    def __configureDelivery(self):

        self.deliveryList = dict()
        if('delivery' in self.config):
            deliveryConfig = self.config['delivery']
        else:
           print("Warning: No delivery mechanisms configured. No images will be saved.")

        for method in deliveryConfig:
            methodName = list(method.keys())[0]
            if(methodName == 'LocalSave'):
                print("LocalSave configured")
                if('directory' in method[methodName]):
                    directory = method[methodName]['directory']
                    self.deliveryList['LocalSave'] = LocalPhotoStorage(directory)
                else:
                    print("No directory specified. Not adding LocalSave to delivery mechanisms")
                    continue
            else:
                print("Unknown delivery mechanism. Not adding")
                continue

    #-----------------------------------------------------------#
    def __configureCamera(self):
        """Get the camera configuration information from the config file and initialize the hardware"""
        print("Initializing camera hardware")
        if('cameraType' in self.config):
            cameraTypeStr = self.config['cameraType']
        else:
            print("No Camera type specified. Defaulting to RPI2")
            cameraTypeStr = "RPI2"

        if(cameraTypeStr == "RPI2"):
            print("Starting RPI2")
            self.camera = PhotoboothCameraPi(self.screenSize.width(), self.screenSize.height())
        elif(cameraTypeStr == "V4L2"):
            print("V4L2 cameras not yet supported.")
            sys.exit()
        else:
            print("Unknown Camera type. ")
            sys.exit()

    #-----------------------------------------------------------#
    def __configureOverlays(self):
        """Configure the overlays based on the config file."""
        if('overlay' in self.config):
            overlayTypeStr = self.config['overlay']
        else:
            print("No Overlay specified. Defaulting to None")
            overlayTypeStr = "None"

        if(overlayTypeStr == "None"):
            print("No Overlay Function Required")
        elif(overlayTypeStr == "Basic"):
            print("Basic Overlay Specified")
            self.camera.overlayFactory = BasicCountdownOverlayFactory(self.resourcePath)
            if('overlayOptions' in self.config):
                oopts = self.config['overlayOptions']
                if('font' in oopts):
                    self.camera.overlayFactory.fontFile = oopts['font']
                if('color' in oopts):
                    self.camera.overlayFactory.setColorHex(oopts['color'])
        else:
            print("Unknown Overlay Type")
            sys.exit()

    #-----------------------------------------------------------#
    def __configureTemplates(self):
        """Get the template information from the config file and initialize the template manager"""
        print("Initializing Templates...")
        if('templateDir' in self.config):
            self.templateDir = self.config['templateDir']
        else:
            print("No template directory specified. Defaulting to ./templates")
            self.templateDir = "./templates"
            
        self.templateManager = TemplateManager(self.templateDir)
    
    #-----------------------------------------------------------#
    def __changeScreens(self, screen):
        """Changes the screens on the gui to the selected screen"""
        print("Changing Screens: " + str(screen))
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
            item.setData(template, Qt.UserRole)
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
        self.templateView.setSelectionMode(QListView.SingleSelection)
        self.templateView.setEditTriggers(QListView.NoEditTriggers)
        self.templateView.clicked.connect(lambda index: self.onTemplateSelected(index))
        self.templateView.setModel(self.templateModel)

    #---------------------------------------------------------#
    def onPhotosTaken(self, photoList):
        #Move to the processing page.
        self.camera.end_preview()
        self.resultImage = self.processor.processImages(photoList)
        self.configureResultScreen()
        self.__changeScreens(QtPyPhotobooth.Screens.RESULT)
        

    #---------------------------------------------------------#
    def onTemplateSelected(self, templateIndex):
        """Handle the event when the user selects a template. """
        #Switch pages and start taking pictures.
        self.__changeScreens(QtPyPhotobooth.Screens.PREVIEW)
        print("Template Selected: " + templateIndex.data())
        template = templateIndex.data(Qt.UserRole)
        self.selectedTemplate = template
        numPhotos = len(template.photoList)
        print("Number of photos to take: " + str(numPhotos))

        #Configure and start the camera
        self.camera.setCaptureResolution(self.selectedTemplate.getMaxImageSize())
        self.camera.start_preview()
        thread = threading.Thread(target=self.camera.capturePhotos, args=(numPhotos, self.onPhotosTaken))
        thread.start()
        self.processor = ImageProcessor(self.selectedTemplate)

    #---------------------------------------------------------#
    def configureResultScreen(self):
        """Place the result image on the result screen."""
        #take the image in question
        imgQt = ImageQt.ImageQt(self.resultImage)
        pixmap = QPixmap.fromImage(imgQt)
        #detatch is required to keep a reference to the image as the imgQt object goes out of scope
        pixmap.detach()

        ######################################
        #Figure out sizing and placement of the label.
        #update main window ui to remove scaled component.
        w = self.resultLabel.width()
        print("Width: " + str(w))
        h = self.resultLabel.height()
        print("Height: " + str(h))
        self.resultLabel.setPixmap(pixmap.scaled(w, h, Qt.KeepAspectRatio))

    #-----------------------------------------------------------------------#
    def onCancelButtonClicked(self):
        """Whenever a cancel button is clicked, go back to the beginning."""
        self.__changeScreens(QtPyPhotobooth.Screens.TEMPLATE)

    #-----------------------------------------------------------------------#
    def onSaveButtonClicked(self):
        """Handle the action of saving or sending the photo through a specific delivery mechanism."""
        self.__changeScreens(QtPyPhotobooth.Screens.SAVING)
        
        thread = threading.Thread(target=self.savePhoto, args=(self.onPhotoSaved,))
        thread.start()

    #-----------------------------------------------------------------------#
    def savePhoto(self, callback):
        """Process all the save methods"""
        
        if('LocalSave' in self.deliveryList):
            print("Saving to local disk.")
            self.deliveryList['LocalSave'].saveImage(self.resultImage)

        callback()

    #-----------------------------------------------------------------------#
    def onPhotoSaved(self):
        """Update the gui to indicate that the photo has been saved."""
        self.__changeScreens(QtPyPhotobooth.Screens.SAVED)
         #Show the saved screen for a specific amount of time before moving on.
         #We are using time because this is run in a separate thread from the ui thread.
        time.sleep(self.splashTime/1000)
        self.__changeScreens(QtPyPhotobooth.Screens.TEMPLATE)

        
        
    
####################################
#Main function
####################################
if(__name__ == '__main__'):
    import sys

    app = QApplication(sys.argv)
    mApplication = QtPyPhotobooth()
    sys.exit(app.exec_())
