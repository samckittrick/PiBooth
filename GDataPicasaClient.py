"""Module for interacting with Google's Picasa Web API.
By: Scott McKittrick


Most APIs require a GDataOauth2Client.OAuth2Token object to use for accessing them. See the appropriate
module for notes on obtaining this token. 

Classes Contained:
PicasaClient - Main class for accessing Picasa APIs

Dependencies:
pycurl
python3-lxml

"""
import GDataOauth2Client
import pycurl
from enum import Enum
from io import BytesIO
from lxml import etree

class MessageTypes(Enum):
    """Message types for callbacks"""
    MSG_SUCCESS = 0
    MSG_FAILED = 1;

class PicasaErrors(Enum):
    #Unknown Error
    ERR_UNKNOWN = 0
    #Error connecting to server
    ERR_NETWORK = 1
    #Malformed Request sent or recieved
    ERR_PROTOCOL = 2
    #Token is invalid, please refresh the token and try again
    ERR_UNAUTHORIZED = 3
    
class PicasaClient:
    """Picasa Client - Main class for accessing the Picasa Web APIs
       Most functions make network calls and require a callback function in the form:
          def callback(messageType, messageData)

       Data formats for MSG_SUCCESS depends on function
       Data formats for MSG_FAILED follow:
          { 'error_type': ERR_UNAUTHORIZED, 'error_string': 'API call could not be authenticated.' }
    """

    def __init__(self, userId="default"):
        """Main constructor. Provide the userID of the account you want to access or detect the one used for the credentials used in the calls.
        Most calls will use the default credentials."""
        
        self.gDataVersion = "3"
        self.userId = userId
        self.picasaBaseURL = "https://picasaweb.google.com/data/feed/api"

        #Used XML namespaces
        self.atomNS = "{http://www.w3.org/2005/Atom}"
        self.googleNS = "{http://schemas.google.com/photos/2007}"

    def getAlbumList(self, token, callback):
        """Retreives a list of albums for the given user.
           Takes:
             token - OAuth Token
             callback - Callback to send list to.
           Calls back with a list of dictionaries with album metadata: """
        url = self.picasaBaseURL + "/user/" + self.userId
        headers = [
            "GData-Version: " + self.gDataVersion,
            "Authorization: Bearer " + token.accessToken]

        buffer = BytesIO()
        c = pycurl.Curl()
        try:
            c.setopt(c.URL, url)
            c.setopt(c.HTTPHEADER, headers)
            c.setopt(c.WRITEDATA, buffer)
            c.perform()

            responseCode = c.getinfo(c.RESPONSE_CODE)
            rspStr = buffer.getvalue()
        except pycurl.error:
            msgData = { 'error_code': PicasaErrors.ERR_NETWORK, 'error_string': c.errstr() }
            callback(MessageTypes.MSG_FAILED, msgData)
        finally:
            c.close()

        if(responseCode == 200):
            print("Parsing response")
            albumList = self.__parseAlbumList(rspStr)
            callback(MessageTypes.MSG_SUCCESS, albumList)
            
        elif(responseCode == 400):
            msgData = { 'error_type': PicasaErrors.ERR_PROTOCOL, 'error_string': rspStr.decode('iso-8859-1') }
            callback(MessageTypes.MSG_FAILED, msgData)
        elif((responseCode == 403) or (responseCode == 401)):
            msgData = { 'error_type': PicasaErrors.ERR_UNAUTHORIZED, 'error_string': rspStr.decode('iso-8859-1') }
            callback(MessageTypes.MSG_FAILED, msgData)
        else:
            msgData = { 'error_type': PicasaErrors.ERR_UNKNOWN, 'error_string': str(responseCode) + ": " + rspStr.deocde('iso-8859-1')}
            callback(MessageTypes.MSG_FAILED, msgData)

    def getPhotoList(self, albumId, token, callback):
        """Retreives a list of albums for the given user.
           Takes:
             token - OAuth Token
             callback - Callback to send list to.
           Calls back with a list of X tuple of album data: """
        url = self.picasaBaseURL + "/user/" + self.userId + "/albumid/" + albumId
        print(url)
        headers = [
            "GData-Version: " + self.gDataVersion,
            "Authorization: Bearer " + token.accessToken]

        buffer = BytesIO()
        c = pycurl.Curl()
        try:
            c.setopt(c.URL, url)
            c.setopt(c.HTTPHEADER, headers)
            c.setopt(c.WRITEDATA, buffer)
            c.perform()

            responseCode = c.getinfo(c.RESPONSE_CODE)
            rspStr = buffer.getvalue()
        except pycurl.error:
            msgData = { 'error_code': PicasaErrors.ERR_NETWORK, 'error_string': c.errstr() }
            callback(MessageTypes.MSG_FAILED, msgData)
        finally:
            c.close()

        if(responseCode == 200):
            print("Parsing response")
            print(rspStr.decode('iso-8859-1'))
        elif(responseCode == 400):
            msgData = { 'error_type': PicasaErrors.ERR_PROTOCOL, 'error_string': rspStr.decode('iso-8859-1') }
            callback(MessageTypes.MSG_FAILED, msgData)
        elif((responseCode == 403) or (responseCode == 401)):
            msgData = { 'error_type': PicasaErrors.ERR_UNAUTHORIZED, 'error_string': rspStr.decode('iso-8859-1') }
            callback(MessageTypes.MSG_FAILED, msgData)
        else:
            msgData = { 'error_type': PicasaErrors.ERR_UNKNOWN, 'error_string': str(responseCode) + ": " + rspStr.deocde('iso-8859-1')}
            callback(MessageTypes.MSG_FAILED, msgData)
            

    def __parseAlbumList(self, xmlFeed):
        """Function for parsing the xmlResponse of the album list. Returns a list of entries """
        entryList = list()
        rspXML = etree.fromstring(xmlFeed)
        entries = rspXML.findall(self.atomNS + "entry")
        for entry in entries:
            entryMeta = self.__parseAlbumListEntry(entry)
            entryList.append(entryMeta)

        return entryList

    def __parseAlbumListEntry(self, entryElement):
        """Function for parsing the entry into a list of metadata"""
        entryMeta = dict()
        entryMeta['title'] = entryElement.find(self.atomNS + "title").text
        entryMeta['albumId'] = entryElement.find(self.googleNS + "id").text
        entryMeta['accessRights'] = entryElement.find(self.atomNS + "rights").text
        entryMeta['author'] = entryElement.find(self.atomNS + "author").find(self.atomNS + "name").text
        return entryMeta
