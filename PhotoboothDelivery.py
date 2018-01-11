"""Module for delivering the final photos from the photobooth. 
By: Scott McKittrick

This module provides classes that will deliver the final photo to the user. 

Classes Contained:
AbstractPhotoboothDelivery - Interface defining delivery mechanism classes
LocalPhotoStorage - Stores the photos in a configured location on the harddrive


"""
import time
import math
import os
from abc import ABC, ABCMeta, abstractmethod

from PyQt5.QtCore import QObject, pyqtSignal

import GDataOauth2Client
from GDataOauth2Client import MessageTypes as GDOMessageTypes
from GDataOauth2Client import OAuth2Token as GDOAuth2Token
from GDataOauth2Client import GDataOAuthError
from GDataPicasaClient import PicasaClient, PicasaErrors
from GDataPicasaClient import MessageTypes as PicasaMessageTypes
from GDataPicasaClient import MetadataTags as GMetadataTags
import json
from pathlib import Path
from enum import Enum
from io import BytesIO

########################################################################
# AbstractPhotoboothDelivery Class                                     #
########################################################################
class AbstractPhotoboothDelivery(QObject):
    """Interface defining basic delivery mechanism functions. """
    __metaclass__ = ABCMeta

    #PyQtSlots
    photoSaveUpdate = pyqtSignal(str, int, int)
    photoSaveComplete = pyqtSignal(str, bool)
    

    #---------------------------------------------------------------------------#
    def __init__(self):
        """Calls the QObject constructor"""
        super().__init__()
    
    #---------------------------------------------------------------------------#
    @abstractmethod
    def saveImage(self, image):
        """ Method to actually save an image. Takes a PIL Image object."""
        pass

    #--------------------------------------------------------------------------#
    @abstractmethod
    def getServiceName(self):
        """Get the name of this service"""
        pass

########################################################################
# LocalPhotoStorage Class                                              #
########################################################################
class LocalPhotoStorage(AbstractPhotoboothDelivery):
    """Class that can be configured for a specified location on the harddrive and saves images to that location."""

    #---------------------------------------------------------------------------#
    def __init__(self, storageLocation):
        """Set up the storage location"""
        super().__init__()
        self.storageLocation = storageLocation
        self.completeHandler = None
        self.serviceName = "Local Storage"

    #---------------------------------------------------------------------------#
    def __generateCollisionResistantName(self, extension):
        """Generates the image filename as 'IMG_<timestamp>.<ext>'"""
        timestamp = int(math.floor(time.time()))
        return "IMG_" + str(timestamp) + "." + extension
        
    #---------------------------------------------------------------------------#
    def saveImage(self, image):
        """Save the image itself. """

        success = False
        try:
            print("Saving image")
            if(not os.path.exists(self.storageLocation)):
                os.makedirs(self.storageLocation)
        
            filename = self.__generateCollisionResistantName("jpg")
            print("Filename: " + filename)
            image.save(self.storageLocation + os.path.sep + filename)
            success = True
        except:
            print("Error saving file")

        if(success):
            self.photoSaveComplete.emit(self.serviceName, True)
        else:
            self.photoSaveComplete.emit(self.serviceName, False)
        

    #---------------------------------------------------------------------------#
    def setUpdateHandler(self, handler):
        """This delivery method does not need progress updates."""
        pass

    #---------------------------------------------------------------------------#
    def setCompleteHandler(self, handler):
        """Implement a notification that the process is complete"""
        self.completeHandler = handler

    #---------------------------------------------------------------------------#
    def getServiceName(self):
        return self.serviceName

#################################################################################
# GooglePhotoStorage                                                            #
#################################################################################
class GooglePhotoStorage(AbstractPhotoboothDelivery):
    """ Photobooth delivery class to send images to Google Photos """

    class StatusMessage(Enum):
        MSG_AUTH_REQUIRED = 0
        MSG_AUTH_SUCCESS = 1
        MSG_AUTH_FAILED = 2
        MSG_ALBUM_LIST = 3
        MSG_UPLOAD_STATUS = 4
        MSG_UNAUTHORIZED = 5
        MSG_REQUEST_SUCCEEDED = 6
        MSG_REQUEST_FAILED = 7

    #PyQt Signals
    messageReceived = pyqtSignal(StatusMessage, object) 
    
    
    #---------------------------------------------------------------------------#
    def __init__(self, clientId, clientSecret, serializedToken,  imgSummary):
        """Initialize the delivery mechanism. Caller should catch any exceptions generated from parsing json input"""

        #Call the parent constructor
        super().__init__()

        self.serviceName = "Google Photos"
        
        #Read in client credentials
        self.clientId = clientId
        self.clientSecret = clientSecret

        self.token = None
        if(serializedToken is not None):
            try:
                self.token = GDOAuth2Token.deserializeToken(serializedToken)
            except Exception as e:
                print("Warning: Invalid token supplied. - " + str(e))
                print("Ignoring supplied token")

        self.imgSummary = imgSummary
        self.configCallback = None
        self.scopeList = [ "https://picasaweb.google.com/data/" ]
        self.albumList = list()
        self.albumListTime = 0 #time the album list was received. for cacheing purposes.
        self.cacheTimeout = 60 #seconds until the cache is not valid anymore
        self.albumId = None

        #Start setting up the clients
        self.oAuthClient = GDataOauth2Client.OAuth2DeviceClient(self.clientId, self.clientSecret, self.scopeList, self.gDataOAuthCallback)
        self.picasaClient = PicasaClient()

    #---------------------------------------------------------------------------#
    def gDataOAuthCallback(self, msgType, msgData):
        """Internal callback for oauth calls"""
        #If the server sends a verification code. 
        if(msgType == GDOMessageTypes.MSG_VERIFICATION_REQUIRED):
            self.messageReceived.emit(self.StatusMessage.MSG_AUTH_REQUIRED, msgData)
        #if the authorization was successful
        elif(msgType == GDOMessageTypes.MSG_OAUTH_SUCCESS):
            #Successful requests return a token.
            self.token = msgData
            
            self.messageReceived.emit(self.StatusMessage.MSG_AUTH_SUCCESS, GDOAuth2Token.serializeToken(self.token))
        #If there was an error
        elif(msgType == GDOMessageTypes.MSG_OAUTH_FAILED):
            #If the token presented caused an error, get a whole new token
            if(((msgData['error_code'] == GDataOAuthError.ERR_CREDENTIALS) or (msgData['error_code'] == GDataOAuthError.ERR_PROTOCOL)) and (self.token is not None)):
                print("Google refresh token failed, trying to get new token.")
                self.oAuthClient.requestAuthorization()
            #otherwise the error can't be recovered
            else:
                self.messageReceived.emit(self.StatusMessage.MSG_AUTH_FAILED, msgData['error_string'])
        else:
            print("Oauth Message: " + str(msgType))

    #---------------------------------------------------------------------------#
    def gDataPhotoCallback(self, msgType, msgData):
        """Internal callback for google photos calls"""
        #print("Data callback : " + str(msgType) + " - " + str(msgData))
        print("Handle refresh token, cache data, compare to current. emit correct signal")
        if(msgType == PicasaMessageTypes.MSG_SUCCESS):
            self.albumList = msgData
            self.albumListTime = time.time()
            #if the requested album id is correct
            if(self.__checkAlbumId(self.requestedAlbumId)):
                print("Album Id selected: " + self.requestedAlbumId)
                self.albumId = self.requestedAlbumId
                self.messageReceived.emit(self.StatusMessage.MSG_REQUEST_SUCCEEDED, None)
            else:
                self.messageReceived.emit(self.StatusMessage.MSG_ALBUM_LIST, self.albumList)
                
        elif(msgType == PicasaMessageTypes.MSG_FAILED):
            if(msgData['error_type'] == PicasaErrors.ERR_UNAUTHORIZED):
                self.messageReceived.emit(self.StatusMessage.MSG_UNAUTHORIZED, None)
            else:
                self.messageReceived.emit(self.StatusMessage.MSG_REQUEST_FAILED, msgData['error_string'])
        
    #---------------------------------------------------------------------------#
    def getAccessToken(self):
        """Take the current token and get a new one. 
           If the token is missing or invalid callback with auth required. if authorization fails, callback with auth failed"""
        if(self.token is not None):
            self.oAuthClient.refreshToken(self.token)
        else:
            self.oAuthClient.requestAuthorization()
        

    #---------------------------------------------------------------------------#
    def setAlbumId(self, albumId = None):
        """ get the album id. Check against the list, if it doesn't match return album_list. Cache album list for future calls. cache timeout 30 seconds"""

        #set the requested album ID
        self.requestedAlbumId = albumId
        
        #get the album Id list if the cache is expired.
        if((time.time() - self.albumListTime) > self.cacheTimeout):
            self.picasaClient.getAlbumList(self.token, self.gDataPhotoCallback)
        else:
            #If the requested album Id is correct
            print("Using cached list")
            if(self.__checkAlbumId(self.requestedAlbumId)):
                self.albumId = self.requestedAlbumId
                self.messageReceived.emit(self.StatusMessage.MSG_REQUEST_SUCCEEDED, None)
            else:
                self.messageReceived.emit(self.StatusMessage.MSG_ALBUM_LIST, self.albumList)
                

    #--------------------------------------------------------------------------#
    def __checkAlbumId(self, albumId):
        """Check to see if the requested album Id is in the albumList"""
        for album in self.albumList:
            if(albumId == album['albumId']):
                return True

        #if we exit the loop, the requested id wasn't found
        return False

    #-------------------------------------------------------------------------#
    def getServiceName(self):
        return self.serviceName

    #-------------------------------------------------------------------------#
    def saveImage(self, image):
        """Upload the image to google photos"""

        #create metadata
        metadata = { GMetadataTags.TAG_SUMMARY: self.imgSummary,
                     GMetadataTags.TAG_TITLE: self.generateCollisionResistantName(".jpg") }

        #Save the image into memory
        buffer = BytesIO()
        image.save(buffer, format='jpeg')
        buffer.seek(0)

        self.uploadCall = lambda: self.picasaClient.uploadPhoto(buffer, metadata, self.albumId, self.token, self.uploadCallback)
        #send the image
        self.messageReceived.connect(self.uploadCallback)
        self.uploadCall()
        self.messageReceived.disconnect(self.uploadCallback)
        
    #-----------------------------------------------------------------------#
    def uploadCallback(self, msgType, data):
        if(msgType == PicasaMessageTypes.MSG_SUCCESS):
            self.photoSaveComplete(self.getServiceName(), True)
        elif(msgType == PicasaMessageTypes.MSG_FAILED):
            if(data['error_type'] == PicasaErrors.ERR_UNAUTHORIZED):
                print("Refresh token")
                self.getAccessToken()
            else:
                self.photoSaveComplete(self.getServiceName(), False)
        elif(msgType == PicasaMessageTypes.MSG_PROGRESS):
            self.photoSaveUpdate.emit(self.getServiceName(), data['total'], data['progress'])
        elif(msgType == self.StatusMessage.MSG_AUTH_SUCCESS):
            self.uploadCall()

    #-----------------------------------------------------------------------#
    def generateCollisionResistantName(self, extension):
        timestamp = int(math.floor(time.time()))
        return "IMG_" + str(timestamp) + "." + extension
