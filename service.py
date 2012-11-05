"""
This is default file of SynopsiTV service. See addon.xml
<extension point="xbmc.service" library="service.py" start="login|startup">
"""
from scrobbler import Scrobbler
from library import RPCListenerHandler
from cache import *
from utilities import home_screen_fill, login_screen
import xbmc, xbmcgui, xbmcaddon
from app_apiclient import AppApiClient
import thread

__addon__  = get_current_addon()
__cwd__    = __addon__.getAddonInfo('path')

def main():
    apiclient1 = AppApiClient.getDefaultClient()
    
    # on first run
    if __addon__.getSetting('FIRSTRUN') == 'true':
        # enable home screen recco
        __addon__.openSettings()
        xbmc.executebuiltin('Skin.SetBool(homepageShowRecentlyAdded)')    
        xbmc.executebuiltin('ReloadSkin()')
        __addon__.setSetting(id='FIRSTRUN', value="false")

    # get or generate install-unique ID
    iuid = get_install_id()

    # try to restore cache  
    cache = StvList(iuid, apiclient1)

    try:
        cache.load(os.path.join(__cwd__, 'resources', 'cache.dat'))
    except:
        # first time
        xbmc.log('CACHE restore failed. If this is your first run, its ok')

    cache.list()

    thread.start_new_thread(home_screen_fill, (apiclient1, cache))

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
    cache.save(os.path.join(__cwd__, 'resources', 'cache.dat'))


if __name__ == "__main__":
    main()
