from agent import SynopsiMovieAgent
# from apiclient import ApiClient
from debug.debug_apiclient import ApiClient

apiclient = ApiClient.getDefaultClient()

def Start():
	Log.Warn('XXX Start')
	apiclient.getAccessToken()
