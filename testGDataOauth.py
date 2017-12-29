import GDataOauth2Client
from GDataOauth2Client import OAuth2Token
import GDataPicasaClient
from GDataPicasaClient import MetadataTags
import sys
from pathlib import Path
import json
import pycurl
from io import BytesIO

#initialize variables
token = None
tokenFilename = ""
credentialsFilename = ""
clientSecret = ""
clientId = ""
scopes = [ "https://picasaweb.google.com/data/" ]
api = GDataPicasaClient.PicasaClient()

#Callback for oauth calls
def oAuthCallback(msgType, params):
    print("Message type: " + str(msgType))
    print("Message Params: \n" + str(params))

    if(msgType == GDataOauth2Client.OAuth2DeviceClient.MessageTypes.MSG_OAUTH_SUCCESS):
        global token
        token = params
        tokenPath = Path(tokenFilename)
        tokenFile = tokenPath.open(mode="w+")
        tokenFile.write(OAuth2Token.serializeToken(token))
        tokenFile.close()

#Callback for albumList calls
def albumListCallback(msgType, params):
    print(msgType)
    if(msgType == GDataPicasaClient.MessageTypes.MSG_SUCCESS):
        i = 1
        for album in params:
            print(str(i) + ") " + album['title'])
            i += 1
        select = input("Select an album: ")

        metadata = {
            MetadataTags.TAG_SUMMARY: "This is a summary",
            MetadataTags.TAG_TITLE: "Title.jpg"
        }
        api.uploadPhoto("testimg.jpg" , metadata, params[int(select) - 1]['albumId'], token, lambda t,d: print("Type: " + str(t) + " - Data: " + str(d)))
    

#Check Arguments
if(len(sys.argv) < 3):
    print("Usage: testGDataOauth.py <credentials file> <Token filename>")
    exit()
else:
    credentialsFilename = sys.argv[1]
    tokenFilename = sys.argv[2]

#Lets read the credentials
credentialPath = Path(credentialsFilename)
credentialFile = credentialPath.open()
credentials = json.loads(credentialFile.read())
clientSecret = credentials['installed']['client_secret']
clientId = credentials['installed']['client_id']

client = GDataOauth2Client.OAuth2DeviceClient(clientId, clientSecret, scopes, oAuthCallback)

#Get an access code either by generating a new token or refreshing the old one.
#read in token file
tokenPath = Path(tokenFilename)

if(tokenPath.is_file()):
    tokenFile = tokenPath.open()
    tokenString = tokenFile.read()
    token = OAuth2Token.deserializeToken(tokenString)
    tokenFile.close()
    client.refreshToken(token)
else:
    client.requestAuthorization()
    


#Test picasa api
api.getAlbumList(token, albumListCallback)

