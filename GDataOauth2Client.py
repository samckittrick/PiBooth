"""Module for OAuth 2.0 tasks for the Google Data APIs
By: Scott McKittrick

Many Google APIs require Authorization to use. Google requires that applications use OAuth 2.0 to allow users to access those APIs.
They provide several methods of using OAuth 2.0 including one intended for applications without rich input interfaces like keyboards.
This module implements classes for handling OAuth2 requests to Google.

Note: This module contains network requests that can be long running. Most calls to it should be done in another thread from the main UI thread 
in a GUI application.

Classes Contained:
OAuth2DeviceClient - The main OAuth 2.0 client
OAuth2DeviceClient.MessageTypes - Messages that the OAuth2DeviceClient can send.
OAuth2Deviceclient.GDataAuthError - Error types that this application can return.
OAuth2Token - A serializable class representing a generic Google OAuth2 Token

Dependencies:
pycurl
"""

from enum import Enum
from io import BytesIO
import pycurl
from urllib.parse import urlencode
import json
import time


############################################################################
# OAuth2DeviceClient                                                       #
############################################################################
class OAuth2DeviceClient:
    """Main class for Google Data API Oauth2.0 Device Clients

Initializing the client:
To initialize the client you need the following information:

- ClientId:
   The ID of your application. You can get this ID from the Google website:
   https://console.developers.google.com/apis/credentials
   You should not share this ID with others as it is specific to your application.

- Client Secret
   The client secret from the console website. Do not share this with others as it is 
   specific to your application and allows your application to authenticate itself to 
   Google's API Servers. 

- Scope List:
   Essentially a list of permissions that your application is requesting to be granted access to. 
   These requests are formatted as URLs and can be found at:
   https://developers.google.com/identity/protocols/googlescopes
   For this client, the list should be formatted as an array of strings.

- Application Callback:
   This callback function is provided by the user of the client. It allows the client to provide status updates to the 
   user even if it is placed in another thread.  It should have the following prototype:
    def callbackFunction(msgType, msgData)

    msgType is an enumerated type as defined by MessageTypes
    msgData is a variable set of data depending on the defined method type.

Message Type definitions:
   MSG_OAUTH_FAILED: 
      Represents various failure conditions
      Example Data format (Note: Error string may not be user friendly.):
         {
            'error_code': <GDataOAuthError.ERR_CREDENTIALS: 3>,
            'error_string': 'invalid_client'
         }            
      
   MSG_VERIFICATION_REQUIRED:
      Indicates that the application needs the user to grant permission. 
      This is the time to display the verification url.
      Example Data format:
         {
            'verification_url': 'https://www.google.com/device', 
            'expires_in': 1800, 
            'user_code': 'DZDR-RHZF'
         }

   MSG_CLIENT_WAITING:
      Indicates that the client has begun polling the server and is 
      waiting for the user to grant permission.
      Example Data Format:
         <Empty set>

   MSG_OAUTH_SUCCESS:
      Indicates that the client has successfully authenticated to the google servers
      Example Data Format:
         <GDataOauth2Client.OAuth2Token object at 0x76a3d230>

Error Types:
   ERR_UNKNOWN = 0 - Thrown for Errors that have not otherwise been identified
   ERR_NETWORK = 1 - Thrown for network errors that prevent pycurl from contacting the server
   ERR_PROTOCOL = 2 - Thrown for protocol errors that prevent successful communication
   ERR_CREDENTIALS = 3 - Thrown if there is something wrong with the provided client ID or secret
   ERR_AUTH_FAILED = 4 - Thrown if the user refuses to authorize a request.

"""

    #######################################################################
    # MessageTypes                                                        #
    #######################################################################
    class MessageTypes(Enum):
        """Enumerated list of message types that the client might send."""
        #Sent if the client requires user verification.
        MSG_VERIFICATION_REQUIRED = 0
        #Sent if the client is waiting for verification and a response from the server
        MSG_CLIENT_WAITING = 1
        #Sent if the oauth was successful
        MSG_OAUTH_SUCCESS = 2
        #sent if the oauth failed.
        MSG_OAUTH_FAILED = 3

    ########################################################################
    # GDataOAuthError                                                      #
    ########################################################################
    class GDataOAuthError(Enum):
        ERR_UNKNOWN = 0
        ERR_NETWORK = 1
        ERR_PROTOCOL = 2
        ERR_CREDENTIALS = 3
        ERR_AUTH_FAILED = 4

    #----------------------------------------------------------------------#
    def __init__(self, clientId, clientSecret, scopeList, applicationCallback):
        """Initialize the device client
        Parameters:
        authServer - URL that the client uses for authorization
        clientId - The id of the client as assigned by google.
        scopeList - an array of requested scope strings for the authorization
        applicationCallback - a callback function that supports two parameters ( MessageType, MessageData)"""

        self.authServer = "https://accounts.google.com/o/oauth2/device/code"
        self.pollServer = "https://www.googleapis.com/oauth2/v4/token"
        self.refreshServer = self.pollServer
        self.grantType = "http://oauth.net/grant_type/device/1.0"
        self.refreshGrantType = "refresh_token"
        self.clientId = clientId
        self.clientSecret = clientSecret
        self.scopeList = scopeList
        self.applicationCallback = applicationCallback
        self.deviceCode = ""
        self.pollInterval = 10

    #---------------------------------------------------------------------#
    def requestAuthorization(self):

        #Set up scope string
        scopeString = self.scopeList[0]
        for i in range(1, len(self.scopeList)):
            scopeString += " " + self.scopeList[i]

        #Create post data
        postData = {'client_id': self.clientId, 'scope': scopeString } 
        postFields = urlencode(postData)
        try:
            #Call curl here
            buffer = BytesIO()
            c = pycurl.Curl()
            c.setopt(c.URL, self.authServer)
            c.setopt(c.POSTFIELDS, postFields)
            c.setopt(c.WRITEDATA, buffer)
            c.perform()

            body = buffer.getvalue()

            responsecode = c.getinfo(c.RESPONSE_CODE)
            reqResp = json.loads(body.decode('iso-8859-1'))

        except pycurl.error as err:
            msgData = { 'error_code': self.GDataOAuthError.ERR_NETWORK, 'error_string': c.errstr() }
            self.applicationCallback(self.MessageTypes.MSG_OAUTH_FAILED, msgData)
            return
        finally:
            c.close()
            
        #Start handling the response.
        if(responsecode == 200):
            msgData = { 'user_code': reqResp['user_code'],
                        'verification_url': reqResp['verification_url'],
                        'expires_in': reqResp['expires_in'] }
            self.interval = reqResp['interval']
            self.deviceCode = reqResp['device_code']
            self.applicationCallback(self.MessageTypes.MSG_VERIFICATION_REQUIRED, msgData)
            self.startPolling()
            
        elif(responsecode == 400):
            msgData = { 'error_code': self.GDataOAuthError.ERR_PROTOCOL, 'error_string': reqResp['error'] }
            self.applicationCallback(self.MessageTypes.MSG_OAUTH_FAILED, msgData)
        elif(responsecode == 401):
            msgData = { 'error_code': self.GDataOAuthError.ERR_CREDENTIALS, 'error_string': reqResp['error'] }
            self.applicationCallback(self.MessageTypes.MSG_OAUTH_FAILED, msgData)
        else:
            msgData = { 'error_code': self.GDataOAuthError.ERR_UNKNOWN, 'error_string': reqResp['error'] }
            self.applicationCallback(self.MessageTypes.MSG_OAUTH_FAILED, msgData)
            
    #-----------------------------------------------------------------------------------------#
    def startPolling(self):
        """ Start polling to wait for the user to grant permission. """

        #Notify the GUI that we are polling
        self.applicationCallback(self.MessageTypes.MSG_CLIENT_WAITING, {} )

        keepPolling = True
        while(keepPolling):
            time.sleep(self.interval)
            postData = {
                'client_id': self.clientId,
                'client_secret': self.clientSecret,
                'code': self.deviceCode,
                'grant_type': self.grantType }
            postFields = urlencode(postData)

            buffer = BytesIO()
            c = pycurl.Curl()
            try:
                c.setopt(c.URL, self.pollServer)
                c.setopt(c.POSTFIELDS, postFields)
                c.setopt(c.WRITEDATA, buffer)
                c.perform()

                responsecode = c.getinfo(c.RESPONSE_CODE)
                reqResp = json.loads(buffer.getvalue().decode('iso-8859-1'))
            except pycurl.error as err:
                msgData = { 'error_code': self.GDataOAuthError.ERR_NETWORK, 'error_string': c.errstr() }
                self.applicationCallback(self.MessageTypes.MSG_OAUTH_FAILED, msgData)
                return
            finally:
                c.close()
            
            if(responsecode == 200):
                keepPolling = False
                expiration = int(time.time()) + int(reqResp['expires_in'])
                token = OAuth2Token(reqResp['refresh_token'], reqResp['token_type'], reqResp['access_token'], expiration)
                self.applicationCallback(self.MessageTypes.MSG_OAUTH_SUCCESS, token)
            elif(responsecode == 400):
                errorType = reqResp['error']
                #The google api has combined legit errors with the "still waiting" response. Need to decide if it's an error or to just try again
                if(errorType == "authorization_pending"):
                    print("Still waiting...")
                else:
                    keepPolling = False
                    msgData = { 'error_code': self.GDataOAuthError.ERR_PROTOCOL, 'error_string': reqResp['error'] + ": " + reqResp['error_description']}
                    self.applicationCallback(self.MessageTypes.MSG_OAUTH_FAILED, msgData)
            elif(responsecode == 403):
                keepPolling = False
                msgData = { 'error_code': self.GDataOAuthError.ERR_AUTH_FAILED, 'error_string': reqResp['error'] + ": User cancelled authorization" }
                self.applicationCallback(self.MessageTypes.MSG_OAUTH_FAILED, msgData)
            elif(responsecode == 429):
                #if we are going too fast. add 2 seconds to the interval
                print("Too fast, increasing interval..")
                self.interval += 2
            else:
                keepPolling = False
                msgData = { 'error_code': self.GDataOAuthError.ERR_UNKNOWN, 'error_string': reqResp['error'] + ": " + reqResp['error_description'] }
                self.applicationCallback(self.MessageTypes.MSG_OAUTH_FAILED, msgData)

    #----------------------------------------------------------------------------------------------------------------------------------------------#
    def refreshToken(self, token):
        """Takes a GDataOauth2Client.OAuth2Token and gets a new accessToken for it. """
        
        postData = { 'refresh_token': token.refreshToken,
                     'client_id': self.clientId,
                     'client_secret': self.clientSecret,
                     'grant_type': self.refreshGrantType }
        postFields = urlencode(postData)

        
        buffer = BytesIO()
        c = pycurl.Curl()
        try:
            c.setopt(c.URL, self.refreshServer)
            c.setopt(c.POSTFIELDS, postFields)
            c.setopt(c.WRITEDATA, buffer)
            c.perform()
            
            responsecode = c.getinfo(c.RESPONSE_CODE)
            reqResp = json.loads(buffer.getvalue().decode('iso-8859-1'))
        except pycurl.error as err:
            msgData = { 'error_code': self.GDataOAuthError.ERR_NETWORK, 'error_string': c.errstr() }
            self.applicationCallback(self.MessageTypes.MSG_OAUTH_FAILED, msgData)
            return
        finally:
            c.close()


        if(responsecode == 200):
            expiration = int(time.time()) + int(reqResp['expires_in'])
            token.accessToken = reqResp['access_token']
            token.expiration = expiration
            token.tokenType =  reqResp['token_type']
            self.applicationCallback(self.MessageTypes.MSG_OAUTH_SUCCESS, token);
        elif(responsecode == 401):
            msgData = { 'error_code': self.GDataOAuthError.ERR_CREDENTIALS, 'error_string': reqResp['error'] }
            self.applicationCallback(self.MessageTypes.MSG_OAUTH_FAILED, msgData)
        elif(responsecode == 400):
            msgData = { 'error_code': self.GDataOAuthError.ERR_PROTOCOL, 'error_string': reqResp['error'] + ": " + reqResp['error_description']}
            self.applicationCallback(self.MessageTypes.MSG_OAUTH_FAILED, msgData)
        else:
            msgData = { 'error_code': self.GDataOAuthError.ERR_UNKNOWN, 'error_string': reqResp['error'] + ": " + reqResp['error_description'] }
            self.applicationCallback(self.MessageTypes.MSG_OAUTH_FAILED, msgData)

####################################################################################################################################################
# OAuth2 Token                                                                                                                                     #
####################################################################################################################################################
class OAuth2Token:
    """This class represents an OAuth token that can be saved and loaded so that it is persistent"""
    
    def __init__(self, refreshToken, tokenType, accessToken=None, expiration=0):
        self.refreshToken = refreshToken
        self.accessToken = accessToken
        self.tokenType = tokenType
        self.expiration = expiration

    #static function
    def serializeToken(token):
        """Serialize the token into a writeable string for saving"""
        struct = { 'refreshToken': token.refreshToken, 'token_type': token.tokenType }
        return json.dumps(struct)

    def deserializeToken(tokenString):
        tokenArr = json.loads(tokenString)
        return OAuth2Token(tokenArr['refreshToken'], tokenArr['token_type'])

    

    
