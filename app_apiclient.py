from apiclient import *
from utilities import *
import threading

class AppApiClient(ApiClient):
	def __init__(self, base_url, key, secret, username, password, device_id, originReqHost=None, debugLvl=logging.INFO, accessTokenTimeout=10, rel_api_url='api/public/1.0/'):
		super(AppApiClient, self).__init__(base_url, key, secret, username, password, device_id, originReqHost, debugLvl, accessTokenTimeout, rel_api_url)
		self._lock_access_token = threading.Lock()

	def getAccessToken(self):
		if not self._lock_access_token.acquire(False):
			xbmc.log('getAccessToken lock NOT acquired')
			return False

		xbmc.log(threading.current_thread().name + ' getAccessToken START')
		finished = False
		while not finished:
			# try to log in
			try:
				ApiClient.getAccessToken(self)
			# in failure, ask for new login/pass and repeat if dialog was not canceled
			except AuthenticationError:
				finished = not login_screen(self)
				xbmc.log('Trying new credentials ? %d' % int(not finished))
			except Exception as e:
				finished = True
				xbmc.log('Another exception')
				xbmc.log(str(e))
			else:
				finished = True
				xbmc.log('Login success')


		xbmc.log(threading.current_thread().name + ' getAccessToken END')
		self._lock_access_token.release()