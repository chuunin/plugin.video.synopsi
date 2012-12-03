"""
This is default file of SynopsiTV service. See addon.xml
<extension point="xbmc.service" library="service.py" start="login|startup">
"""
# xbmc
import xbmc, xbmcgui, xbmcaddon

# python standart lib
import thread

# application
from scrobbler import Scrobbler
from library import RPCListenerHandler
from cache import *
from utilities import home_screen_fill, login_screen, log
from app_apiclient import AppApiClient
from addonservice import AddonService

__addon__  = get_current_addon()
__cwd__	= __addon__.getAddonInfo('path')

DEFAULT_SERVICE_PORT=9091

def main():
	apiclient1 = AppApiClient.getDefaultClient()

	# check first run
	check_first_run()

	# get or generate install-unique ID
	iuid = get_install_id()

	# try to restore cache
	cache = StvList(iuid, apiclient1)

	try:
		cache.load()
	except:
		# first time
		log('CACHE restore failed. If this is your first run, its ok')
		cache.rebuild()

	#~ cache.list()

	thread.start_new_thread(home_screen_fill, (apiclient1, cache))

	s = Scrobbler(cache)
	l = RPCListenerHandler(cache, s)
	aos = AddonService('localhost', DEFAULT_SERVICE_PORT, apiclient1, cache)
	s.start()
	l.start()
	aos.start()

	log('Entering service loop')
	while True:
		s.join(0.5)
		l.join(0.5)

		if not l.isAlive() and not s.isAlive() and not s.isAlive():
			log('Service loop end. Both threads are dead')
			break

		if xbmc.abortRequested:
			log('service.py abortRequested')
			aos.stop()
			break;

	log('library and scrobbler quit')
	cache.save()


if __name__ == "__main__":
	main()
