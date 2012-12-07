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

	def getAccessToken(self):
		if not self._lock_access_token.acquire(False):
			log('getAccessToken lock NOT acquired')
			return False

		#~ log(threading.current_thread().name + ' getAccessToken START')
		finished = False
		while not finished:
			try:
				# clear tokens if user credentials changed
				if self.reloadUserPass():
					self.clearAccessToken()

				# try to log in
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
				log('Unknown exception')
				log(str(e))
			else:
				finished = True
				log('Login success')


		#~ log(threading.current_thread().name + ' getAccessToken END')
		self._lock_access_token.release()

	# convienent functions
	def get_unwatched_episodes(self):
		episodes = self.unwatchedEpisodes()

		# log('unwatched episodes')
		# for title in episodes['lineup']:
		#	 log(title['name'])

		result = episodes['lineup']
		return result

	def get_upcoming_episodes(self):
		episodes = self.unwatchedEpisodes()

		# log('upcoming episodes')
		# for title in episodes['upcoming']:
		#	 log(title['name'])

		result = episodes['upcoming']
		return result

