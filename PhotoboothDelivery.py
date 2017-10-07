"""Module for delivering the final photos from the photobooth. 
By: Scott McKittrick

This module provides classes that will deliver the final photo to the user. 

Classes Contained:
LocalPhotoStorage - Stores the photos in a configured location on the harddrive


"""
import time
import math
import os

########################################################################
# LocalPhotoStorage Class                                              #
########################################################################
class LocalPhotoStorage:
    """Class that can be configured for a specified location on the harddrive and saves images to that location."""

    #---------------------------------------------------------------------------#
    def __init__(self, storageLocation):
        """Set up the storage location"""
        self.storageLocation = storageLocation

    #---------------------------------------------------------------------------#
    def __generateCollisionResistantName(self, extension):
        """Generates the image filename as 'IMG_<timestamp>.<ext>'"""
        timestamp = int(math.floor(time.time()))
        return "IMG_" + str(timestamp) + "." + extension
        
    #---------------------------------------------------------------------------#
    def saveImage(self, image):
        """Save the image itself. Does not catch exceptions. The calling function should do so."""

        print("Saving image")
        if(not os.path.exists(self.storageLocation)):
            os.makedirs(self.storageLocation)
        
        filename = self.__generateCollisionResistantName("jpg")
        print("Filename: " + filename)
        image.save(self.storageLocation + os.path.sep + filename)
