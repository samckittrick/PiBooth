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
import json
from pathlib import Path
from enum import Enum

########################################################################
# AbstractPhotoboothDelivery Class                                     #
########################################################################
class AbstractPhotoboothDelivery(QObject):
    """Interface defining basic delivery mechanism functions. """
    __metaclass__ = ABCMeta
    
    #---------------------------------------------------------------------------#
    @abstractmethod
    def saveImage(self, image):
        """ Method to actually save an image. Takes a PIL Image object."""
        pass

    #---------------------------------------------------------------------------#
    @abstractmethod
    def setUpdateHandler(self, handler):
        """Set the callback function for updates. The callback prototype should be:
        def callback(serviceName, total, progress) """
        pass

    #--------------------------------------------------------------------------#
    @abstractmethod
    def setCompleteHandler(self, handler):
        """Set the save complete handler. Callback prototype should be:
        def callback(serviceName) """
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

        if(self.completeHandler is not None):
            self.completeHandler(self.serviceName, success)
        

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
        MSG_UPLOAD_SUCCESS = 5
        MSG_UPLOAD_FAILED = 6
        
    
    #---------------------------------------------------------------------------#
    def __init__(self, clientId, clientSecret, serializedToken,  imgSummary):
        """Initialize the delivery mechanism. Caller should catch any exceptions generated from parsing json input"""

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
        self.albumList = None
        self.albumListTime = 0

        #Start setting up the clients
        self.oAuthClient = GDataOauth2Client.OAuth2DeviceClient(self.clientId, self.clientSecret, self.scopeList, self.gDataOAuthCallback)

    #---------------------------------------------------------------------------#
    def gDataOAuthCallback(self, msgType, msgData):
        """Internal callback for oauth calls"""
        #If the server sends a verification code. 
        if(msgType == GDOMessageTypes.MSG_VERIFICATION_REQUIRED):
            self.configCallback(self.StatusMessage.MSG_AUTH_REQUIRED, msgData)
        #if the authorization was successful
        elif(msgType == GDOMessageTypes.MSG_OAUTH_SUCCESS):
            #Successful requests return a token.
            self.token = msgData
            
            self.configCallback(self.StatusMessage.MSG_AUTH_SUCCESS, GDOAuth2Token.serializeToken(self.token))
        #If there was an error
        elif(msgType == GDOMessageTypes.MSG_OAUTH_FAILED):
            #If the token presented caused an error, get a whole new token
            if(((msgData['error_code'] == GDataOAuthError.ERR_CREDENTIALS) or (msgData['error_code'] == GDataOAuthError.ERR_PROTOCOL)) and (self.token is not None)):
                print("Google refresh token failed, trying to get new token.")
                self.oAuthClient.requestAuthorization()
            #otherwise the error can't be recovered
            else:
                self.configCallback(self.StatusMessage.MSG_AUTH_FAILED, msgData['error_string'])
        else:
            print("Oauth Message: " + str(msgType))
        
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
        pass

    #---------------------------------------------------------------------------#
    def setConfigurationCallback(self, callback):
        """The callback for configuration actions. Prototype:
           def callback(msgType, data) """
        self.configCallback = callback
