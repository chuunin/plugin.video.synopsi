from agent import SynopsiMovieAgent
from apiclient import ApiClient

apiclient = ApiClient()

def Start():
	apiclient.getAccessToken()
	Log.Warn('XXX Start')
