# This might have to move to a 'tools' submodule

#===============
#=== Imports ===
#===============
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials

from requests import Session

from ..loggingBase import getSubLoggerFor

#==================
#=== Exceptions ===
#==================
class spotifyAuthorizationError(Exception): pass

#========================
#=== Module Variables ===
#========================

# masterClient keeps the last logged-in client object in memory for persistance
masterClient = None

# logger
logger = getSubLoggerFor('authorization')

#===============
#=== Classes ===
#===============

def getSpotifyClient(clientId = None, clientSecret = None):
    global masterClient

    # check if inputs are valid and usable
    credentialsProvided = (clientId != None) and (clientSecret != None)
    validInput = credentialsProvided or (masterClient != None)

    # if not valid input, raise error, else either pass on cached client or
    # create a new one as required
    if not validInput:
        logger.critical('Could not authorize Spotify Credentials, no' +
        ' clientId, clientSecret provided')
        raise spotifyAuthorizationError ('You must pass a clientId and' +
        ' clientSecret to this method when authenticating for first time')

    # Note that None can be used as False
    elif masterClient:
        logger.info('Returning cached Spotify Credentials')
    
    else:
        logger.info('Creating authorized Spotify Client >')
        # Oauth
        credentialManager = SpotifyClientCredentials(
            client_id = clientId,
            client_secret = clientSecret
        )
        spotifyClient = Spotify(client_credentials_manager = credentialManager)
        # Cache current client
        masterClient = spotifyClient
    
        logger.info('Client successfully created')
    
    return masterClient