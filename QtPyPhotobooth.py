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
from PyQt5.QtCore import QTimer,QObject, QSize, Qt, pyqtSlot, QThread
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QPixmap, QIcon, QImage

import mainwindow
from PhotoboothCamera import PhotoboothCameraPi, BasicCountdownOverlayFactory
from PhotoboothTemplate import TemplateManager, ImageProcessor
from PhotoboothDelivery import LocalPhotoStorage
from PhotoboothDelivery import GooglePhotoStorage
from pathlib import Path
import json

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

    #-----------------------------------------------------------#    
    def __init__(self, application):
        """QtPyPhotobooth constructor. """
        super(QtPyPhotobooth, self).__init__()

        self.application = application

        #initialise some members
        self.resourcePath = "." + os.path.sep + "res"
        self.defaultTemplateIcon = "defaultTemplateIcon.png"
        self.templateModel = None
        self.gPhotoMessageBox = None
        #this is the list of services the image is saved to and their status
        #format 2-Tuple (ServiceName, True (success)/False (failure))
        self.saveList = list()
        
        print("Initializing configuration...")
        self.configFilename = "config.yaml"
        f = open(self.configFilename, 'r')
        self.config = yaml.load(f)

        #Get some configuration from the config file
                #Show the splash screen for a specific amount of time before moving on.
        if('splashScreenTime' in self.config):
            self.splashTime = self.config['splashScreenTime']
        else:
            print("No Splash Screen Time specified. Defaulting to 5 seconds")
            self.splashTime = 5000

        if('cacheLocation' in self.config):
            self.cacheLocation = os.path.normpath(os.path.abspath(os.path.expanduser(self.config['cacheLocation'])))
        else:
            print("No cache location provided using current working directory.")
            self.cacheLocation = os.getcwd()
        print("Cache Location: " + self.cacheLocation)
        
        print("Intializing  Gui...")
        self.screenSize = self.application.desktop().screenGeometry()
        self.form = mainwindow.MainGuiWindow(self.screenSize.width(), self.screenSize.height(), self.resourcePath + os.path.sep + "logo.jpg")
        print("add logo to yaml configuration. ")
        
        self.form.initUI()

        #Start pulling references to important widgets
        self.mainWindow = self.form.mainWindow
        self.templateLabel = self.form.templateSelectLabel
        self.stackedWidget = self.form.stackedWidget
        self.templateView = self.form.templateView
        #self.resultLabel = self.form.resultImageLabel
        #self.saveButton = self.form.SaveButton
        #self.cancelButton = self.form.CancelButton

        #configure some buttons
        #self.cancelButton.clicked.connect(lambda: self.onCancelButtonClicked())
        #self.saveButton.clicked.connect(lambda: self.onSaveButtonClicked())

        #Now is the time to start showing the splash screen. There will be several triggers that have
        # to happen before the splash screen can change
        #splash trigger count represents the number of items that need to be completed before the splash screen is changed
        self.splashTriggerCount = 0
        self.splashTriggerMutex = threading.Lock()

        #Show the splash Screen
        self.__changeScreens(QtPyPhotobooth.Screens.SPLASH)
        self.form.showMainWindow()

        #Set the minimum time trigger
        #Note: this is the minimum time because there may be other tasks to do before the splash changes.
        self.__incrementSplashTriggerCount()
        self.timer = QTimer()
        self.timer.setInterval(self.splashTime)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.__decrementSplashTriggerCount)
        self.timer.start()

        #Add to the splash count for the rest of the configuration tasks
        self.__incrementSplashTriggerCount()
                                                
        #Configure the camera
        self.__configureCamera()

        #Configure overlays
        self.__configureOverlays()
                
        #Configure the template list.
        self.__configureTemplates()
        self.__configureTemplateView()

        #configure delivery mechanisms
        self.__configureDelivery()

        #The tasks this function needs to complete before it returns have been completed or handed off to other threads
        #It can now remove its trigger from the splash trigger count.
        self.__decrementSplashTriggerCount()





        #-----------------------------------------------------------#
    def __incrementSplashTriggerCount(self):
        self.splashTriggerMutex.acquire(True)
        self.splashTriggerCount += 1
        print("Splash Trigger Count is now: " + str(self.splashTriggerCount))
        self.splashTriggerMutex.release()

    #-----------------------------------------------------------#
    def __decrementSplashTriggerCount(self):
        self.splashTriggerMutex.acquire(True)
        self.splashTriggerCount -= 1
        print("Splash Trigger Count is now: " + str(self.splashTriggerCount))
        if(self.splashTriggerCount is 0):
            self.__changeScreens(QtPyPhotobooth.Screens.TEMPLATE)
        self.splashTriggerMutex.release()

    #-----------------------------------------------------------#
    def __configureDelivery(self):

        print("Configuring delivery mechanisms")

        self.deliveryList = list()
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
                    self.deliveryList.append(LocalPhotoStorage(directory))
                else:
                    print("No directory specified. Not adding LocalSave to delivery mechanisms")
                    continue
            elif(methodName == 'GooglePhotos'):
                print("GooglePhotos configured")
                gphotoMethod = method[methodName]

                #start parsing out parameters
                if('credentialsFile' in gphotoMethod):
                    credentialsFilename = os.path.normpath(os.path.abspath(os.path.expanduser(gphotoMethod['credentialsFile'])))
                    try:
                        credentialsFile = Path(credentialsFilename).open('r')
                        credentialsJSON = json.loads(credentialsFile.read())
                        clientId = credentialsJSON['installed']['client_id']
                        clientSecret = credentialsJSON['installed']['client_secret']
                        print("Google Photos credentials file found")
                    except Exception as e:
                        print("Warning: Error opening credentials file - " + str(e))
                        print("Not adding Google Photos as delivery mechanism")
                        continue
                else:
                    print("Warning: Google Photos configured but no credentials supplied. Not adding Google Photos to delivery mechanisms")
                    continue

                #Get the image summary to be sent to google photos with every image.
                imgSummary = "Created with QtPyPhotobooth"
                if('imgSummary' in gphotoMethod):
                    imgSummary = gphotoMethod['imgSummary']

                #Tokens from previous sessions should be loaded
                tokenFilename = os.path.join(self.cacheLocation, "gphotoToken.txt")
                serializedToken = None
                try:
                    tokenFile = Path(tokenFilename).open('r')
                    serializedToken = tokenFile.read()
                    print("Google Photos authentication token read")
                except Exception as e:
                    print("Warning: Error reading token file. - " + str(e))
                    print("Token file may not exist or is not accessible. This may be expected. You Will need to start OAuth2 process")

                #Get the AlbumId if there is one
                self.gPhotoAlbumId = None

                self.gPhotoDelivery = GooglePhotoStorage(clientId, clientSecret, serializedToken, imgSummary)
                self.gPhotoDelivery.messageReceived.connect(self.googlePhotosConfigCallback)

                self.__incrementSplashTriggerCount()
                mThread = threading.Thread(target=self.gPhotoDelivery.getAccessToken)
                mThread.start()
                
            else:
                print("Unknown delivery mechanism. Not adding")
                continue

    #-----------------------------------------------------------#
    @pyqtSlot(GooglePhotoStorage.StatusMessage, object)
    def googlePhotosConfigCallback(self, msgType, data):
        """Callback for configuring the google photos delivery mechanism. Since configuring it requires network calls, we use threads and callbacks to complete it."""

        #print("GData Config Callback: " + str(msgType) + " - " + str(data))
        if(msgType == self.gPhotoDelivery.StatusMessage.MSG_UNAUTHORIZED):
            #If it is unauthorized, we need to refresh the token
            mThread = threading.Thread(target=self.gPhotoDelivery.getAccessToken)
            mThread.start()
        if(msgType == self.gPhotoDelivery.StatusMessage.MSG_AUTH_REQUIRED):
            print("Google Photos OAuth2 Device Code received.")
            self.gPhotoMessageBox = self.__buildGDataOAuthCodeDialog(data['user_code'], data['verification_url'])
            self.gPhotoMessageBox.exec_()
        elif(msgType == self.gPhotoDelivery.StatusMessage.MSG_AUTH_SUCCESS):
            print("Token Received. Saving...")
            try:
                if(self.gPhotoMessageBox is not None):
                    self.gPhotoMessageBox.done(1)
                tokenFilename = os.path.join(self.cacheLocation, "gphotoToken.txt")
                tokenFile = Path(tokenFilename).open('w+')
                tokenFile.write(data)
                tokenFile.close()
                
            except Exception as e:
                print("Error saving token - " + str(e))
                print("You will have to reauthorize next time this application is run.")

            #Lets try setting the albumId again
            mThread = threading.Thread(target=self.gPhotoDelivery.setAlbumId, args=[self.gPhotoAlbumId])
            mThread.start()
        elif(msgType == self.gPhotoDelivery.StatusMessage.MSG_AUTH_FAILED):
            print("Authorization Failed")
            self.gPhotoMessageBox.done(1)
            self.gPhotoMessageBox = QMessageBox(self.mainWindow)
            self.gPhotoMessageBox.setText("Authorization Failed. Google Photos will not be added as a delivery mechanism.")
            self.gPhotoMessageBox.exec_()
            self.__decrementSplashTriggerCount()

        elif(msgType == self.gPhotoDelivery.StatusMessage.MSG_ALBUM_LIST):
            print("Defaulting to a specific id")
            self.gPhotoMessageBox = self.__buildGDataAlbumSelector(data)
            self.gPhotoMessageBox.exec_()
            print("Album Selected: " + self.gPhotoMessageBox.getSelected().text())
            self.gPhotoAlbumId = self.gPhotoMessageBox.getSelected().data(Qt.UserRole)
            mThread = threading.Thread(target=self.gPhotoDelivery.setAlbumId, args=[self.gPhotoAlbumId])
            mThread.start()
        elif(msgType == self.gPhotoDelivery.StatusMessage.MSG_REQUEST_SUCCEEDED):
            print("Google Photos Delivery Mechanism Configured. Adding...")
            self.deliveryList.append(self.gPhotoDelivery)
            self.gPhotoDelivery.messageReceived.disconnect(self.googlePhotosConfigCallback)
            self.__decrementSplashTriggerCount()
        else:
            print("Unknown error. Not Adding google photos to delivery list")
            self.__decrementSplashTriggerCount()
            

    #-----------------------------------------------------------#
    def __buildGDataOAuthCodeDialog(self, code, verificationURL):
        """Builds the custom dialog for showing the OAuth2 Device authorization code to the user."""
        mBox = QDialog(self.mainWindow)
        #mBox.setTitle("Google Photos OAuth Device Code")
        winSize = self.mainWindow.size()
        mBox.setFixedSize(QSize(winSize.width()/2, winSize.height()/2))
        mBox.setModal(True)
        mBox.setWindowTitle("Google Photos Authorization")
        #mBox.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.FramelessWindowHint | Qt.Dialog)

        vLay = QVBoxLayout()
        vLay.setAlignment(Qt.AlignCenter)
        vLay.addStretch(1)
        l = QLabel("<h2>QtPy Photobooth needs permission to access your Google Photos account.<h2>")
        l.setAlignment(Qt.AlignCenter)
        l.setWordWrap(True)
        vLay.addWidget(l)

        vLay.addStretch(1)
        l = QLabel("<h1>" + code + "<h1>")
        l.setAlignment(Qt.AlignCenter)
        vLay.addWidget(l)
        vLay.addStretch()

        l = QLabel("Please enter the code at the following URL: <br />" + verificationURL)
        l.setAlignment(Qt.AlignCenter)
        vLay.addWidget(l)
        mBox.setLayout(vLay)
        return mBox

    #-----------------------------------------------------------#
    def __buildGDataAlbumSelector(self, albumList):
        """Builds the selection dialog for selecting an album"""
        listLabel = "<h2>Please select an album to upload picture to</h2>"
        itemList = list()
        for album in albumList:
            item = QListWidgetItem()
            item.setText(album['title'])
            item.setData(Qt.UserRole, album['albumId'])
            itemList.append(item)
        
        mBox = QBasicListSelector(self.mainWindow, listLabel, itemList)
        winSize = self.mainWindow.size()
        mBox.setFixedSize(QSize(winSize.width()/2, winSize.height()/2))
        mBox.setModal(True)
        mBox.setWindowTitle("Google Photos Album Selection")
        
        return mBox
        

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
            self.templateDir = os.path.normpath(os.path.abspath(os.path.expanduser(self.config['templateDir'])))
        else:
            print("No template directory specified. Defaulting to ./templates")
            self.templateDir = os.path.normpath(os.path.abspath("templates"))
            
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
        self.templateView.setIconSize(QSize(200,200))
        #self.templateView.setUniformItemSizes(True)
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
        requestedPhotos = list()
        for p in template.photoList:
            requestedPhotos.append((p['width'],p['height']))

        #Configure and start the camera
        self.camera.setCaptureResolution(requestedPhotos[0])
        self.camera.start_preview()
        thread = threading.Thread(target=self.camera.capturePhotos, args=(requestedPhotos, self.onPhotosTaken))
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
        
        for method in self.deliveryList:
            print("Saving to " + method.getServiceName())
            method.photoSaveUpdate.connect(self.updateHandler)
            method.photoSaveComplete.connect(self.completeHandler)
            method.saveImage(self.resultImage)
        callback()

    #-----------------------------------------------------------------------#
    def updateHandler(self, serviceName, total, progress):
        """ Handle upload/save events from the delivery method"""
        print("Update: " + serviceName + " - " + str(progress) + "/" + str(total))

    #-----------------------------------------------------------------------#
    def completeHandler(self, serviceName, success):
        """ Allows the delivery method to indicate that it has completed saving/uploading the photo"""
        print("Save to " + serviceName + " " + ("successful." if success else  "failed."))
        self.saveList.append((serviceName, success))

    #-----------------------------------------------------------------------#
    def onPhotoSaved(self):
        """Update the gui to indicate that the photo has been saved."""
        self.__changeScreens(QtPyPhotobooth.Screens.SAVED)
         #Show the saved screen for a specific amount of time before moving on.
         #We are using time because this is run in a separate thread from the ui thread.
        time.sleep(self.splashTime/1000)
        self.__changeScreens(QtPyPhotobooth.Screens.TEMPLATE)

####################################################################################
# QBasicListSelector                                                               #
####################################################################################
class QBasicListSelector(QDialog):
    """Basic list selection dialog"""

    #----------------------------------------------------------------------#
    def __init__(self, parent, label, itemList):
        super().__init__(parent)
        
        self.listLabel = QLabel(label)
        self.listWidget = QListWidget()
        
        #Create the layout and add the first label
        vLay = QVBoxLayout()
        vLay.setAlignment(Qt.AlignCenter)
        vLay.addWidget(self.listLabel)

        #Add the list widget
        for item in itemList:
            self.listWidget.addItem(item)
        vLay.addWidget(self.listWidget)

        #Create the button and place it in a horizontal box
        hLay = QHBoxLayout()
        okButton = QPushButton("Ok")
        okButton.clicked.connect(self.closeDialog)
        hLay.addStretch(1)
        hLay.addWidget(okButton)
        vLay.addLayout(hLay)

        #Add the vertical layout
        self.setLayout(vLay)

        #Select the first item by default
        self.listWidget.setCurrentItem(itemList[0])

    #---------------------------------------------------------------------#
    def closeDialog(self):
        self.accept()

    #---------------------------------------------------------------------#
    def getSelected(self):
        return self.listWidget.currentItem()
        
        
####################################
#Main function
####################################
if(__name__ == '__main__'):
    import sys

    app = QApplication(sys.argv)
    mApplication = QtPyPhotobooth(app)
    sys.exit(app.exec_())
