from apiclient import *
from utilities import *

class AppApiClient(ApiClient):
	def getAccessToken(self):
		finished = False
		while not finished:
			# try to log in
			try:
				ApiClient.getAccessToken(self)
			# in failure, ask for new login/pass and repeat if dialog was not canceled
			except AuthenticationError:
				finished = not login_screen()
				xbmc.log('Trying new credentials')
			else:
				finished = True
				xbmc.log('Login success')
