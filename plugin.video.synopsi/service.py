"""
This is default file of SynopsiTV service. See addon.xml
<extension point="xbmc.service" library="service.py" start="login|startup">
"""
from library import Library
from cache import *
import xbmc, xbmcgui, xbmcaddon
from scrobbler import *

__addon__  = xbmcaddon.Addon()

def main():

    # try to restore cache  
    cacheSer = __addon__.getSetting(id='CACHE')

    try:
        cache = deserialize(cacheSer)
    except:
        # first time init
        xbmc.log('CACHE restore failed. If this is your first run, its ok')
        cache = Cache()

    cache.list()

    p = SynopsiPlayerDecor()
    p.setCache(cache)

    l = Library(cache)
    l.start()

    xbmc.log('Entering service loop')

    while True:
        l.join(0.5)

    xbmc.log('library quit')

    __addon__.setSetting(id='CACHE', value=serialize(cache))


if __name__ == "__main__":
    main()
