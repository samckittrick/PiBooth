"""Configuration Module for photobooth
By: Scott McKittrick

Eventually will be populated using PyYaml

Dependencies: 
None

Classes contained:
PhotoboothConfig - Configuration class

"""

#############################################################
# PhotoboothConfig class                                    #
#############################################################
class PhotoboothConfig:

    def __init__(self):
        self.templateLocation = "./templates"
        self.splashScreenTime = 1000

    def getTemplateLocation(self):
        return self.templateLocation;

    def getSplashScreenTime(self):
        return self.splashScreenTime
