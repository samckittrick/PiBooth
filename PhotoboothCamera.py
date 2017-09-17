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
import picamera
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
    def __init__(self, previewWidth, previewHeight):
        """PhotoboothCamera constructor"""
        self.countDownLength = 5
        self.resultShowTime = 2
        self.camera = picamera.PiCamera()
        self.photoList = list()
        self.previewWidth = previewWidth
        self.previewHeight = previewHeight
        self.overlay = None #give it the overlay later.

    #-----------------------------------------------------#
    def setCountdownLength(self, len):
        self.countDownLength = len

    #-----------------------------------------------------#
    def setResultShowTime(self, len):
        self.resultShowTime = len

    #-----------------------------------------------------#
    def __timerTriggered(self):
        """Do the next step in the state machine. This will happen once a second for (count down time * number of photos) seconds."""
        if(self.__currentCountDown == 0):
            #If we are at the end of a countdown.
            #Capture the image, add it to the list and reset the countdown
            pass

        else:
            #update the overlay and state machine.
            self.__updateOverlay(self.__currentCountDown)
            self.__currentCountDown -= self.__currentCountDown

    #----------------------------------------------------#
    def __updateOverlay(self, currentNumber):
        if(isinstance(self.overlay, BasicCountdownOverlayFactory)):
            oImg = self.overlay.getOverlayImage(currentNumber, self.previewWidth, self.previewHeight)

            #One difficulty of working with overlay renderers is that they expect unencoded RGB input which is padded
            #up to the camera’s block size. The camera’s block size is 32x16 so any image data provided to a renderer
            #must have a width which is a multiple of 32, and a height which is a multiple of 16. The specific RGB
            #format expected is interleaved unsigned bytes. If all this sounds complicated, don’t worry; it’s quite
            #simple to produce in practice.
            #Padding up to the required size
            paddedImg = Image.new(oImg.mode, (
                ((oImg.size[0] + 31) // 32) * 32,
                ((oImg.size[1] + 15) // 16) * 16,
                ))
            paddedImg.paste(oImg, (0, 0))
            
            #create overlay behind, then flip and remove old one
            #Pillow Image object uses upper case mode names (e.g. "RGBA") but picamera uses lower case (e.g. "rgba")
            self.__overlayHandle = self.camera.add_overlay(paddedImg.tobytes(), oImg.size, oImg.mode.lower())
            self.__overlayHandle.layer = 3

        else:
            print("Overlay is wrong type or doesn't exist")
            

    #-----------------------------------------------------#
    def capturePhotos(self, numPhotos):
        #photo capture uses a simple state machine. Initialize it here.
        self.__photosLeft = numPhotos
        self.__currentCountDown = self.countDownLength

        self.camera.start_preview()
        print("Camera resolution:")
        print(self.camera.resolution)
        self.__timerTriggered()
        #Add QTimer here to continue the countdown
        


#################################################################
# BasicCounddownOverlayFactory                                  #
#################################################################
class BasicCountdownOverlayFactory:
    """Basic class to generate overlay images for countdowns

    Customizable parameters:
    fontSize
    fontFile
    fillColor

    This class may be subclassed and its functions overriden to change its behavior"""

    #-----------------------------------------------------#
    def __init__(self, resDir):
        """Initialize overlay with default info."""
        self.fontSize = 500
        self.fontFile = resDir + os.path.sep + "LuckiestGuy.ttf"
        self.fillColor = (0,0,0,255)


    #-----------------------------------------------------#
    def getOverlayImage(self, text, width, height):
        """Take a string of text, and generate an image centered on screen"""
        #Calculate the size of the image.
        font = ImageFont.truetype(self.fontFile, self.fontSize)
        im = Image.new("RGBA", (width, height), (0,0,0,0))

        #Actually draw the text on the image.
        draw = ImageDraw.Draw(im)
        w,h = draw.textsize(str(text), font)
        print("Overlay: Width: " + str(w) + " Height: " + str(h))
        draw.text(((width-w)/2,(height-h)/2), str(text), self.fillColor, font)
        return im
