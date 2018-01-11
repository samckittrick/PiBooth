"""Module for interacting with Google's Picasa Web API.
By: Scott McKittrick


Most APIs require a GDataOauth2Client.OAuth2Token object to use for accessing them. See the appropriate
module for notes on obtaining this token. 

Classes Contained:
PicasaClient - Main class for accessing Picasa APIs
MessageTypes - Messages that can be sent to the callbacks
PicasaErrors - Error Codes for the callbacks
MetadataTags - Supported tags that can be sent to Google Photos

Dependencies:
pycurl
python3-lxml

"""
import GDataOauth2Client
import pycurl
from enum import Enum
from io import BytesIO, IOBase
from lxml import etree
from lxml.etree import QName

#####################################################################################################
# MessageTypes - Types of messages that will be sent to the callback function                       #
#####################################################################################################
class MessageTypes(Enum):
    """Message types for callbacks"""
    MSG_SUCCESS = 0
    MSG_FAILED = 1
    MSG_PROGRESS = 2

#####################################################################################################
# PicasaErrors - Error codes for the callbacks                                                      #
#####################################################################################################
class PicasaErrors(Enum):
    #Unknown Error
    ERR_UNKNOWN = 0
    #Error connecting to server
    ERR_NETWORK = 1
    #Malformed Request sent or recieved
    ERR_PROTOCOL = 2
    #Token is invalid, please refresh the token and try again
    ERR_UNAUTHORIZED = 3

#####################################################################################################
# MetadataTags - Supported tags that can be sent to Google Photos                                   #
#####################################################################################################
class MetadataTags(Enum):
    TAG_TITLE = 0
    TAG_SUMMARY = 1

#####################################################################################################
# PicasaClient                                                                                      #
#####################################################################################################
class PicasaClient:
    """Picasa Client - Main class for accessing the Picasa Web APIs
       Most functions make network calls and require a callback function in the form:
          def callback(messageType, messageData)

       Data formats for MSG_SUCCESS depends on function
       Data formats for MSG_FAILED follow:
          { 'error_type': ERR_UNAUTHORIZED, 'error_string': 'API call could not be authenticated.' }
    """
    #----------------------------------------------------------------------------------------------#
    def __init__(self, userId="default"):
        """Main constructor. Provide the userID of the account you want to access or detect the one used for the credentials used in the calls.
        Most calls will use the default value which pulls the account from the credentials."""
        
        self.gDataVersion = "3"
        self.userId = userId
        self.picasaBaseURL = "https://picasaweb.google.com/data/feed/api"

        #Used XML namespaces
        self.googleNamespaces = {
            "atom":         "http://www.w3.org/2005/Atom",
            "gd":         "http://schemas.google.com/g/2005",
            #"openSearch": "http://http://a9.com/-/spec/opensearch/1.1/",
            "gphoto":     "http://schemas.google.com/photos/2007",
            "app":        "http://w3.org/2007/app",
            "exif":       "http://schemas.google.com/photos/exif/2007",
            "media":      "http://search.yahoo.com/mrss/" }

    #---------------------------------------------------------------------------------------------#
    def getAlbumList(self, token, callback):
        """Retreives a list of albums for the given user.
           Takes:
             token - OAuth Token
             callback - Callback to send list to.
           Calls back with a list of dictionaries with album metadata. Ex:
           {'albumId': '10000000000000000', 'accessRights': 'protected', 'author': 'Scott McKittrick', 'title': 'Auto Backup'}"""
        url = self.picasaBaseURL + "/user/" + self.userId
        if token is not None:
            headers = [
                "GData-Version: " + self.gDataVersion,
                "Authorization: Bearer " + str(token.accessToken)]
        else:
            headers = [ "GData-Version: " + self.gDataVersion ]

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
            return
        finally:
            c.close()

        if(responseCode == 200):
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

    #---------------------------------------------------------------------------------------------#
    def getPhotoList(self, albumId, token, callback):
        """Retreives a list of albums for the given user.
           Takes:
             token - OAuth Token
             callback - Callback to send list to.
           This function is only partially implemented for testing purposes. """
        url = self.picasaBaseURL + "/user/" + self.userId + "/albumid/" + albumId
        print(url)
        headers = [
            "GData-Version: " + self.gDataVersion ]
        if(token is not None):
            headers.append("Authorization: Bearer " + str(token.accessToken))

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
            return
        finally:
            c.close()

        if(responseCode == 200):
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

    #----------------------------------------------------------------------------------------------------#
    def uploadPhoto(self, photo, metadata, albumId, token, callback):
        """Uploads a photo to the specified album. Calls back progress and result. 
           Parameters:
             -photo - Filename or file like object to send. 
             -metadata - A dictionary of metadata values. The keys should be taken from the MetadataTags class
             -albumId - The ID of the google photo album to send to.
             -token - The GDataOauth2Client.OAuth2Token to authorize the call
             -callback - The callback function for updates to be sent to.

        Note: metadata is currently required.

        Callback Messages :
           MessageTypes.MSG_PROGRESS - Used to show transfer progress. Example data:
              {'total': 587651, 'progress': 99070}
           MessageTypes.MSG_SUCCESS - Indicates the upload was successful. Data is 'NoneType'
        """
        #Generate metadata to be sent
        xmlString = self.__generateMetadataXML(metadata)

        headers = [
            "GData-Version: " + self.gDataVersion,
            "Content-Type: multipart/related"
        ]

        if token is not None:
            headers.append("Authorization: Bearer " + str(token.accessToken))

        data = [
            ( 'metadata', (pycurl.FORM_CONTENTS, xmlString, pycurl.FORM_CONTENTTYPE, 'application/atom+xml'))
        ]


        #Check to see if this is a filename or a file like object
        if(isinstance(photo, IOBase)):
            data.append(('file', (pycurl.FORM_BUFFERPTR, photo.getvalue(), pycurl.FORM_CONTENTTYPE, "image/jpeg")))
        else:
            data.append(('file', (pycurl.FORM_FILE, photo, pycurl.FORM_CONTENTTYPE, "image/jpeg")))

        #Send the file and get the response.
        url = self.picasaBaseURL + "/user/" + self.userId + "/albumid/" + albumId
        try:
            buffer = BytesIO()
            c = pycurl.Curl()
            c.setopt(c.POST, 1)
            c.setopt(c.URL, url)
            c.setopt(c.WRITEDATA, buffer)
            c.setopt(c.HTTPHEADER, headers)
            c.setopt(c.HTTPPOST, data)

            #Add progress updates
            c.setopt(c.NOPROGRESS, False)
            c.setopt(c.XFERINFOFUNCTION, lambda dt, dp, ut, up: callback(MessageTypes.MSG_PROGRESS, self.__makeProgressUpdate(dt, dp, ut, up))) 
            c.perform()

            responseCode = c.getinfo(c.RESPONSE_CODE)
            rspStr = buffer.getvalue()
        except pycurl.error:
            msgData = { 'error_code': PicasaErrors.ERR_NETWORK, 'error_string': c.errstr() }
            callback(MessageTypes.MSG_FAILED, msgData)
            return
        finally:
            c.close()

        if(responseCode == 201):
            print("Upload successful")
        elif(responseCode == 400):
            msgData = { 'error_type': PicasaErrors.ERR_PROTOCOL, 'error_string': rspStr.decode('iso-8859-1') }
            callback(MessageTypes.MSG_FAILED, msgData)
        elif((responseCode == 403) or (responseCode == 401)):
            msgData = { 'error_type': PicasaErrors.ERR_UNAUTHORIZED, 'error_string': rspStr.decode('iso-8859-1') }
            callback(MessageTypes.MSG_FAILED, msgData)
        else:
            msgData = { 'error_type': PicasaErrors.ERR_UNKNOWN, 'error_string': str(responseCode) + ": " + rspStr.deocde('iso-8859-1')}
            callback(MessageTypes.MSG_FAILED, msgData)

    #----------------------------------------------------------------------------------------------------#
    def __makeProgressUpdate(self, download_total, download_progress, upload_total, upload_progress):
        """Send a progress update to the gui. This function is used to format the update into the message format for this class"""
        if(download_total > 0):
            total = download_total
            progress = download_progress
        else:
            total = upload_total
            progress = upload_progress

        return { 'total': total, 'progress': progress }

    #----------------------------------------------------------------------------------------------------#
    def __generateMetadataXML(self, metadata):
        """Function to generate metadata xml for image uploads to the google picasa api.
           The api will only accept certain tags, so the MetadataTag class will help prevent invalid tags from being sent. """

        #Create the root element tag
        root = etree.Element(QName(self.googleNamespaces['atom'], "entry"), nsmap=self.googleNamespaces)

        #Build the category tag
        category = etree.SubElement(root, QName(self.googleNamespaces['atom'], "category"), nsmap=self.googleNamespaces)
        category.set("scheme", self.googleNamespaces['gd'] + "#kind")
        category.set("term", self.googleNamespaces['gphoto'] + "#photo")

        #Insert some metadata.
        for key, value in metadata.items():
            if(key == MetadataTags.TAG_TITLE):
                title = etree.SubElement(root, QName(self.googleNamespaces['atom'], "title"), nsmap=self.googleNamespaces)
                title.text = value
            elif(key == MetadataTags.TAG_SUMMARY):
                summary = etree.SubElement(root, QName(self.googleNamespaces['atom'], "summary"), nsmap=self.googleNamespaces)
                summary.text = value

        return etree.tostring(root)
        

    #----------------------------------------------------------------------------------------------------#
    def __parseAlbumList(self, xmlFeed):
        """Function for parsing the xmlResponse of the album list. Returns a list of entries """
        entryList = list()
        rspXML = etree.fromstring(xmlFeed)
        entries = rspXML.findall("atom:entry", namespaces=self.googleNamespaces)
        for entry in entries:
            entryMeta = self.__parseAlbumListEntry(entry)
            entryList.append(entryMeta)

        return entryList
    
    #----------------------------------------------------------------------------------------------------#
    def __parseAlbumListEntry(self, entryElement):
        """Function for parsing the entry into a list of metadata"""
        entryMeta = dict()
        entryMeta['title'] = entryElement.find("atom:title", namespaces=self.googleNamespaces).text
        entryMeta['albumId'] = entryElement.find("gphoto:id", namespaces=self.googleNamespaces).text
        entryMeta['accessRights'] = entryElement.find("atom:rights", namespaces=self.googleNamespaces).text
        entryMeta['author'] = entryElement.find("atom:author", namespaces=self.googleNamespaces).find("atom:name", namespaces=self.googleNamespaces).text
        return entryMeta
