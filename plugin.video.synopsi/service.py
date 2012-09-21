"""
This is default file of SynopsiTV service. See addon.xml
<extension point="xbmc.service" library="service.py" start="login|startup">
"""
from scrobbler import Scrobbler
from library import Library
from cache import Cache

def main():
	cache = Cache()
	s = Scrobbler(cache)
	s.start()
	l = Library(cache)
	l.start()

if __name__ == "__main__":
    main()
