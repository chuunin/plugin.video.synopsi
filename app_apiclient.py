from apiclient import *
from utilities import *
import threading
import xbmcgui

class AppApiClient(ApiClient):
	def __init__(self, base_url, key, secret, username, password, device_id, originReqHost=None, debugLvl=logging.INFO, accessTokenTimeout=10, rel_api_url='api/public/1.0/'):
		super(AppApiClient, self).__init__(base_url, key, secret, username, password, device_id, originReqHost, debugLvl, accessTokenTimeout, rel_api_url)
		self._lock_access_token = threading.Lock()
		self._rejected_to_correct = False

	def reloadUserPass(self):
		__addon__ = get_current_addon()
		self.username = __addon__.getSetting('USER')
		self.password = __addon__.getSetting('PASS')

	def getAccessToken(self):
		if not self._lock_access_token.acquire(False):
			xbmc.log('getAccessToken lock NOT acquired')
			return False

		xbmc.log(threading.current_thread().name + ' getAccessToken START')
		finished = False
		while not finished:
			# try to log in
			try:
				self.reloadUserPass()
				ApiClient.getAccessToken(self)
				# raise AuthenticationError
				notification('Logged in as %s' % self.username)
			# in failure, ask for new login/pass and repeat if dialog was not canceled
			except AuthenticationError:
				# crashes
				# finished = not login_screen(self)
				if self._rejected_to_correct:
					notification('Authentication failed. Correct your login/password in plugin settings')
				else:
					if xbmcgui.Dialog().yesno("SynopsiTV", "Authentication failed", "Would you like to open settings and correct your login info?"):
						addon = get_current_addon()
						addon.openSettings()
						self.setUserPass(addon.getSetting('USER'), addon.getSetting('PASS'))
					else:
						self._rejected_to_correct = True

				finished = True
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