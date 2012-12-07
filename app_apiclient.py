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
		changed = False

		if self.username != __addon__.getSetting('USER'):
			self.username = __addon__.getSetting('USER')
			changed = True

		if self.password != __addon__.getSetting('PASS'):
			self.password = __addon__.getSetting('PASS')
			changed = True

		return changed

	def clearAccessToken(self):
		self.accessToken = None
		self.accessTokenSessionStart = None

	def checkUserPass(self):
		if self.reloadUserPass():
			self.clearAccessToken()
			return True

		return False

	def isAuthenticated(self):
		" Returns true if user is authenticated. This method adds to its parent method a check if user credentials have changed "
		self.checkUserPass()
		return ApiClient.isAuthenticated(self)

	def getAccessToken(self):
		if not self._lock_access_token.acquire():
			self._log.debug('getAccessToken lock NOT acquired')
			return False
		else:
			self._log.debug(threading.current_thread().name + ' getAccessToken LOCK ACQUIRED')

		finished = False
		while not finished:
			try:
				# check to clear tokens if user credentials changed
				self.checkUserPass()

				# try to log in
				ApiClient.getAccessToken(self)
				if self.login_state_announce==LoginState.Notify:
					notification('Logged in as %s' % self.username)

			# in failure, ask for new login/pass and repeat if dialog was not canceled
			except AuthenticationError:
				if self.login_state_announce==LoginState.Notify:
					if self._rejected_to_correct:
						notification('Authentication failed. Correct your login/password in plugin settings')
						res = False
						finished = True
					else:
						if not dialog_check_login_correct():
							self._rejected_to_correct = True
							res = False
							finished = True

				elif self.login_state_announce==LoginState.AddonDialog:
					raise

			except Exception as e:
				finished = True
				self._log.debug('Unknown exception')
				self._log.debug(str(e))
				res = False
			else:
				finished = True
				self._log.debug('Login success')
				res = True

		self._log.debug(threading.current_thread().name + ' getAccessToken LOCK RELEASE')
		self._lock_access_token.release()
		return res

	# convienent functions
	def get_unwatched_episodes(self):
		episodes = self.unwatchedEpisodes()

		# self._log.debug('unwatched episodes')
		# for title in episodes['lineup']:
		#	 self._log.debug(title['name'])

		result = episodes['lineup']
		return result

	def get_upcoming_episodes(self):
		episodes = self.unwatchedEpisodes()

		# self._log.debug('upcoming episodes')
		# for title in episodes['upcoming']:
		#	 self._log.debug(title['name'])

		result = episodes['upcoming']
		return result

