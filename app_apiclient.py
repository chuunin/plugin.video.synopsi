from apiclient import *
from utilities import *

class AppApiClient(ApiClient):
	def __init__(self, base_url, key, secret, username, password, device_id, originReqHost=None, debugLvl=logging.INFO, accessTokenTimeout=10, rel_api_url='api/public/1.0/'):
		super(AppApiClient, self).__init__(base_url, key, secret, username, password, device_id, originReqHost, debugLvl, accessTokenTimeout, rel_api_url)

	def getAccessToken(self):
		finished = False
		while not finished:
			# try to log in
			try:
				super(AppApiClient, self).getAccessToken()
			# in failure, ask for new login/pass and repeat if dialog was not canceled
			except AuthenticationError:
				finished = not login_screen()
				xbmc.log('Trying new credentials ? %d' % int(not finished))
			except Exception as e:
				finished = True
				xbmc.log('Another exception')
				xbmc.log(str(e))
			else:
				finished = True
				xbmc.log('Login success')

		xbmc.log('Exited getAccessToken')