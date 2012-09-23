"""
This is default file of SynopsiTV service. See addon.xml
<extension point="xbmc.service" library="service.py" start="login|startup">
"""
from scrobbler import Scrobbler
from library import Library
from cache import *
import xbmc, xbmcgui, xbmcaddon

__addon__  = xbmcaddon.Addon()

def main():
	
	cacheSer = __addon__.getSetting(id='CACHE')
	xbmc.log('CACHE/SERIALIZED/ ' + cacheSer)
	cache = deserialize(cacheSer)
	#cache = Cache()
	cache.list()

	s = Scrobbler(cache)
	s.start()
	l = Library(cache)
	l.start()

	xbmc.log('Entering service loop')
	while True:
		s.join(1)
		if s.isAlive():
			xbmc.log('scrobbler join wait')

		l.join(1)
		if l.isAlive():
			xbmc.log('library join wait')

		if not l.isAlive() and not s.isAlive():
			break

		if xbmc.abortRequested:
			xbmc.log('service.py abortRequested')
			break;

	xbmc.log('library and scrobbler quit')

	__addon__.setSetting(id='CACHE', value=serialize(cache))


if __name__ == "__main__":
    main()
