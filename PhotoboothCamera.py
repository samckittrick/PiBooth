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
import time
from io import BytesIO
from abc import ABC, ABCMeta, abstractmethod
import picamera
from PIL import Image, ImageFont, ImageDraw, ImageOps

###################################################################
# AbstractPhotoboothCamera                                        #
###################################################################
class AbstractPhotoboothCamera:
    """Interface representing the camera allowing for photos to be taken
    Provides a state machine for manipulating the video stream. """
    __metaclass__ = ABCMeta

    #----------------------------------------------------------#
    def __init__(self):
        self.countDownLength = 5
        self.resultShowLength = 3
        self.imgList = list()
        self.resetState()

    #-----------------------------------------------------------#
    def resetState(self):
        """Reset the state machine to the base state"""
        self.currentCountdown = self.countDownLength
        self.displayImage = False

    #-----------------------------------------------------------#
    def capturePhotos(self, numPhotos, callback):
        """Step through the state machine
        Parameters:
        numPhotos - The number of photos to take
        callback - A callable that takes a list as the argument"""
        self.resetState()
        while True:
            #if we are still counting down, just continue
            if(self.currentCountdown > 0):
                self.updateOverlay()
                self.currentCountdown -= 1
            
            #if we are done counting down, we need to change state
            else:
                #if we are displaying the countdown, it's time to take a picture
                if(not self.displayImage):
                    self.removeOverlay()
                    self.takePicture()
                    self.displayImage = True
                    self.updateOverlay()
                    self.currentCountdown = self.resultShowLength
                #if we are displaying a result image
                else:
                    #if wehave enough images
                    if(len(self.imgList) >= numPhotos):
                        self.removeOverlay()
                        break
                    #otherwise take another
                    else:
                        self.currentCountdown = self.countDownLength
                        self.displayImage = False
            time.sleep(1)
        #return the list of images
        callback(self.imgList)

    #-----------------------------------------------------------#
    @abstractmethod
    def updateOverlay(self):
        """Function for updating the overlay displayed on screen"""
        pass
    
    #-----------------------------------------------------------#
    @abstractmethod
    def removeOverlay(self):
        """Function for hiding the overlay altogether"""
        pass

    #-----------------------------------------------------------#
    @abstractmethod
    def takePicture(self):
        """Actually capture an image"""
        pass

    #-----------------------------------------------------------#
    @abstractmethod
    def start_preview(self):
        """Do whatever functions it takes to start the preview stream"""
        pass

    #-----------------------------------------------------------#
    @abstractmethod
    def end_preview(self):
        """Do whatever functions it takes to end the preview stream"""
        pass

####################################################################
# PhotoboothCameraPi class                                         #
####################################################################
class PhotoboothCameraPi(AbstractPhotoboothCamera):
    """Implementation of the AbstractPhotoboothCamera using the raspberry pi camera module 2.0 and PiCamera
    Since PiCamera isn't easily integrated with QT, I am doing some of the Gui stuff here. """
    #-------------------------------------------------#
    def __init__(self, previewWidth, previewHeight):
        super().__init__()
        self.camera = picamera.PiCamera()
        self.previewWidth = previewWidth
        self.previewHeight = previewHeight
        self.overlayFactory = None
        self.__overlayHandle = None

    #-------------------------------------------------#
    def start_preview(self):
        self.camera.start_preview()

    #-------------------------------------------------#
    def end_preview(self):
        self.camera.stop_preview()

    #-------------------------------------------------#
    def updateOverlay(self):
        #show the countdown
        if((not self.displayImage) and (self.overlayFactory != None)):
            oImg = self.overlayFactory.getOverlayImage(self.currentCountdown, self.previewWidth, self.previewHeight)
                
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
            tmpOverlayHandle = self.camera.add_overlay(paddedImg.tobytes(), oImg.size, oImg.mode.lower())
            if(self.__overlayHandle != None):
                self.__overlayHandle.layer = 1
            tmpOverlayHandle.layer = 3
            if(self.__overlayHandle != None):
                self.camera.remove_overlay(self.__overlayHandle)
            self.__overlayHandle = tmpOverlayHandle
        #show the result image
        elif(self.displayImage):
            #scale the image to not take the entire screen
            resultImage = ImageOps.expand(self.imgList[-1], 5, "black")
            scaleFactor = 0.75
            scaledSize = ((self.previewWidth * scaleFactor), (self.previewHeight * scaleFactor))
            resultImage.thumbnail(scaledSize)

            #place it on a transparent field the full screen size
            paddedImg = Image.new('RGBA', (
                ((self.previewWidth + 31) // 32) * 32,
                ((self.previewHeight + 15) // 16) * 16,
                ))
            paddedImg.paste(resultImage, ((self.previewWidth - resultImage.size[0]) // 2, (self.previewHeight - resultImage.size[1]) // 2 ))

            #Create the overlay behind and then flip and remove the old one.
            tmpOverlayHandle = self.camera.add_overlay(paddedImg.tobytes(), (self.previewWidth, self.previewHeight), 'rgba')
            if(self.__overlayHandle != None):
                self.__overlayHandle.layer = 1
            tmpOverlayHandle.layer = 3
            if(self.__overlayHandle != None):
                self.camera.remove_overlay(self.__overlayHandle)
            self.__overlayHandle = tmpOverlayHandle
            
            
    #-----------------------------------------------------#
    def removeOverlay(self):
        if(self.__overlayHandle != None):
            self.camera.remove_overlay(self.__overlayHandle)
            self.__overlayHandle = None

    #-----------------------------------------------------#
    def takePicture(self):
        print("Taking Picture")
        stream = BytesIO()
        self.camera.capture(stream, "jpeg")
        stream.seek(0)
        self.imgList.append(Image.open(stream))


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
        draw.text(((width-w)/2,(height-h)/2), str(text), self.fillColor, font)
        return im
