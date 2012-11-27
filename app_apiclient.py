from apiclient import *
from utilities import *
import threading
import xbmcgui

class LoginState:
	Notify = 1
	AddonDialog = 2

class AppApiClient(ApiClient):
	def __init__(self, base_url, key, secret, username, password, device_id, originReqHost=None, debugLvl=logging.INFO, accessTokenTimeout=10, rel_api_url='api/public/1.0/', lsa=LoginState.Notify):
		super(AppApiClient, self).__init__(base_url, key, secret, username, password, device_id, originReqHost, debugLvl, accessTokenTimeout, rel_api_url)
		self._lock_access_token = threading.Lock()
		self._rejected_to_correct = False
		self.login_state_announce = lsa

	def reloadUserPass(self):
		__addon__ = get_current_addon()
		self.username = __addon__.getSetting('USER')
		self.password = __addon__.getSetting('PASS')

	def getAccessToken(self):
		if not self._lock_access_token.acquire(False):
			log('getAccessToken lock NOT acquired')
			return False

		log(threading.current_thread().name + ' getAccessToken START')
		finished = False
		while not finished:
			# try to log in
			try:
				self.reloadUserPass()
				ApiClient.getAccessToken(self)
				if self.login_state_announce==LoginState.Notify:
					notification('Logged in as %s' % self.username)		

			# in failure, ask for new login/pass and repeat if dialog was not canceled
			except AuthenticationError:
				# this crashes
				# finished = not login_screen(self)
				if self.login_state_announce==LoginState.Notify:
					if self._rejected_to_correct:
						notification('Authentication failed. Correct your login/password in plugin settings')
					else:
						if not dialog_check_login_correct():
							self._rejected_to_correct = True
							
					finished = True

				elif self.login_state_announce==LoginState.AddonDialog:
					raise

			except Exception as e:
				finished = True
				log('Another exception')
				log(str(e))
			else:
				finished = True
				log('Login success')


		log(threading.current_thread().name + ' getAccessToken END')
		self._lock_access_token.release()
