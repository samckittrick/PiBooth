"""Module representing the camera to be used in the photobooth.
By: Scott McKittrick

Dependencies:
PiCamera

Classes Contained:
AbstractPhotoboothCamera - Photobooth camera interface
PhotoboothCameraPi - Raspberry Pi Camera Module Class 
BasicCountdownOverlayFactory - Factory object for creating countdown overlays
 """
import os
from abc import ABC, ABCMeta, abstractmethod
from picamera import PiCamera
from PIL import Image, ImageFont, ImageDraw

###################################################################
# AbstractPhotoboothCamera                                        #
###################################################################
class AbstractPhotoboothCamera:
    """Interface representing the camera allowing for photos to be taken"""
    __metaclass__ = ABCMeta

    #-------------------------------------------------------------#
    @abstractmethod
    def setCountdownLength(self, length):
        """Set the number of seconds the countdown should last before capturing the photo"""
        pass

    #------------------------------------------------------------#
    @abstractmethod
    def setResultShowtime(self, length):
        """Set the number of seconds the resultant image should be displayed before starting the next countdown"""
        pass

    #-----------------------------------------------------------#
    @abstractmethod
    def capturePhotos(numPhotos):
        """Capture the requested number of photos. 
        numPhotos - number of photos to be captured
        return - List containing pixmaps of photos"""
        pass
    
####################################################################
# PhotoboothCameraPi class                                         #
####################################################################
class PhotoboothCameraPi(AbstractPhotoboothCamera):
    """Implementation of the AbstractPhotoboothCamera using the raspberry pi camera module 2.0 and PiCamera"""
    #-----------------------------------------------------#
    def __init__(self):
        """PhotoboothCamera constructor"""
        self.camera = PiCamera()
        self.countDownLength = 5
        self.resultShowTime = 2
        self.photoList = list()
        self.overlay = BasicCountdownOverlayFactory()

    #-----------------------------------------------------#
    def setCountdownLength(self, len):
        self.countDownLength = len

    #-----------------------------------------------------#
    def setResultShowTime(self, len):
        self.resultShowTime = len

    #-----------------------------------------------------#
    def capturePhotos(numPhotos):
        pass


#################################################################
# BasicCounddownOverlayFactory                                  #
#################################################################
class BasicCountdownOverlayFactory:
    """Basic class to generate overlay images for countdowns"""

    #-----------------------------------------------------#
    def __init__(self, resDir):
        """Initialize overlay with default info."""
        self.fontFile = resDir + os.path.sep + "LuckiestGuy.ttf"
        self.fontSize = 20
        self.fillColor = (0,0,0,255)


    #-----------------------------------------------------#
    def getOverlayImage(self, text, width, height):
        """Take a string of text, and generate an image centered on screen"""
        #Calculate the size of the image.
        font = ImageFont.truetype(self.fontFile, self.fontSize)
        im = Image.new("RGBA", (width, height), (0,0,0,0))
        draw = ImageDraw.Draw(im)
        w,h = draw.textsize(text, font)
        draw.text(((width-w)/2,(height-h)/2), text, fill=self.fillColor)
        return im
