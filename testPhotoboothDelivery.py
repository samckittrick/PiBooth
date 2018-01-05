import PhotoboothDelivery
from PhotoboothDelivery import GooglePhotoStorage
import sys

def configCallback(msgType, data):
    print("MSGType: " + str(msgType) + " - " + str(data))

#Check Arguments
if(len(sys.argv) < 3):
    print("Usage: testGDataOauth.py <credentials file> <Token filename>")
    exit()
else:
    credentialsFilename = sys.argv[1]
    tokenFilename = sys.argv[2]

delivery = GooglePhotoStorage(credentialsFilename, tokenFilename, "Hello World")
delivery.setConfigurationCallback(configCallback)
delivery.getAccessToken()


