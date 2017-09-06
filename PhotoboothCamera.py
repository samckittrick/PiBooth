"""Module representing the camera to be used in the photobooth.
By: Scott McKittrick

Dependencies:
PiCamera

Classes Contained:
PhotoboothCamera - Main camera class

 """

from picamera import PiCamera

####################################################################
# PhotoboothCamera class                                           #
####################################################################
class PhotoboothCamera:

    #-----------------------------------------------------#
    def __init__(self):
        """PhotoboothCamera constructor"""
        self.camera = PiCamera()
        
    
