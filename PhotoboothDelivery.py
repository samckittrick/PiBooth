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

########################################################################
# AbstractPhotoboothDelivery Class                                     #
########################################################################
class AbstractPhotoboothDelivery:
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
