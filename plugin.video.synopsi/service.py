"""
This is default file of SynopsiTV service. See addon.xml
<extension point="xbmc.service" library="service.py" start="login|startup">
"""
from scrobbler import Scrobbler
from library import RPCListenerHandler
from cache import *
import xbmc, xbmcgui, xbmcaddon

__addon__  = xbmcaddon.Addon()

def main():

    # try to restore cache  
    cacheSer = __addon__.getSetting(id='CACHE')

#   cacheSer = ''   # once per library change, to reinit the serialzed object

    try:
        cache = deserialize(cacheSer)
    except:
        # first time init
        xbmc.log('CACHE restore failed. If this is your first run, its ok')
        cache = StvList()

    cache.list()

    s = Scrobbler(cache)
    l = RPCListenerHandler(cache)
    s.start()
    l.start()

    xbmc.log('Entering service loop')
    while True:
        s.join(0.5)
        l.join(0.5)

        if not l.isAlive() and not s.isAlive():
            xbmc.log('Service loop end. Both threads are dead')
            break

        if False and xbmc.abortRequested:
            xbmc.log('service.py abortRequested')
            break;

    xbmc.log('library and scrobbler quit')

    __addon__.setSetting(id='CACHE', value=serialize(cache))


if __name__ == "__main__":
    main()
