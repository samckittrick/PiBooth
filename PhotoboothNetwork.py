"""Network APIs for photo delivery
By: Scott McKittrick

Supported APIs:
Shutterfly

Dependencies:
PyQt5

Classes Contained:
OAuthLocalServer - Local Web Server for OAuth Callbacks
ShutterflyClient - Client Class for Shutterfly API
AbstractNetworkClient - Client Interface for network clients

"""
import datetime, pytz, hashlib
from abc import ABC, ABCMeta, abstractmethod
from PyQt5.QtWidgets import QDialog

################################################################################
# AbstractNetworkClient                                                        #
################################################################################
class AbstractNetworkClient:
    """Interface for network based delivery methods. """

    __metaclass__ = ABCMeta

    @abstractmethod
    #--------------------------------------------------------------------------#
    def uploadImage(self, image):
        """Uploads an image to the network service
        Takes a PIL Image
        Returns True on success, False on Failure """
        pass

    @abstractmethod
    #--------------------------------------------------------------------------#
    def connectToService(self):
        """Checks to see if the application is authorized to upload. If it's not,
        it will attempt to get authorization.
        Returns True if authorized, false otherwise."""
        pass

    
################################################################################
# ShutterflyClient                                                             #
################################################################################
class ShutterflyClient(AbstractNetworkClient):
    """Client class for interacting with the shutterfly API"""

    #--------------------------------------------------------------------------#
    def __init__(self, appId, remoteUser, sharedSecret, hashMethod):
        """Initialize the Shutterfly client object"""
        self.appId = appId
        self.remoteUser = remoteUser
        self.sharedSecret = sharedSecret
        self.hashMethod = hashMethod

    #-------------------------------------------------------------------------#
    def uploadImage(self, image):
        pass

    #-------------------------------------------------------------------------#
    def connectToService(self):
        pass

    #-------------------------------------------------------------------------#
    def __getTimestamp(self, time):
        """Generates the formatted timestamp to be used in a shutterfly call signature.
        Parameters: time - Datetime representing the time to be formatted"""
        self.timeFormat = '{:%Y-%m-%dT%H:%M:%S.000%z}'
        return self.timeFormat.format(time)

    #-------------------------------------------------------------------------#
    def __calculateSignature(self, urlParams, uri, timeString):
        """Calculates the signature for call signing
        Parameter:
           urlParams - Dictionary of parameters used in the api call
           uri - The uri that isbeing called with leading slash but no trailing slash
           timeString - the formatted timestring to be used as a timestamp"""

        #Begin building the unhashed signature string
        sigString = self.sharedSecret + uri
        first = True
        for key in sorted(urlParams.keys()):
            if(first):
                sigString = '{0}?{1}={2}'.format(sigString, key, urlParams[key])
                first = False
            else:
                sigString = '{0}&{1}={2}'.format(sigString, key, urlParams[key])

        #Adding the oflySig parameters
        sigString = '{0}&{1}={2}'.format(sigString, 'oflyAppId', self.appId)
        sigString = '{0}&{1}={2}'.format(sigString, 'oflyHashMeth', self.hashMethod)
        sigString = '{0}&{1}={2}'.format(sigString, 'oflyTimestamp', timeString)
        print(sigString)
        #Hash the result
        byteArr = sigString.encode('utf-8')

        digest = hashlib.sha1()
        digest.update(byteArr)
        result = digest.digest()
        return ''.join('{:02x}'.format(x) for x in result) 

    #-------------------------------------------------------------------------#
    def __generateSignatureParams(self, urlParams, uri):
        """Generates the signature parameters to be appended to any shutterfly call"""
        timeString = self.__getTimestamp(datetime.datetime.now(pytz.utc))
        signature = self.__calculateSignature(urlParams, uri, timeString)


################################################################################
# ShutterflyConfigDialog                                                       #
################################################################################
class ShutterflyConfigDialog(QDialog):
    """Class for displaying and entering configuration information for the 
    shutterfly service."""



if __name__ == '__main__':
    shutterfly = ShutterflyClient('123456789123456789123456789123', '2', 'asecretsasecrets','SHA1')
    params = {'cParam':'hello', 'aParam': 'goodbye', 'bParam':'wie gehts' }
    print("SigString: " + shutterfly.calculateSignature(params, '/path/to/api'))
