from agent import SynopsiMovieAgent
from apiclient import apiclient

apiclient = ApiClient()

def Start():
	apiclient.getAccessToken()
	Log.Warn('XXX Start')
