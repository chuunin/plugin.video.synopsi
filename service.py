"""
This is default file of SynopsiTV service. See addon.xml
<extension point="xbmc.service" library="service.py" start="login|startup">
"""
from scrobbler import Scrobbler
from library import RPCListenerHandler
from cache import *
from utilities import home_screen_fill, login_screen
import xbmc, xbmcgui, xbmcaddon, xbmcplugin
from app_apiclient import AppApiClient
from addonservice import AddonService
import thread
import logging
import socket
import addon_utilities
import time

__addon__  = get_current_addon()
__cwd__    = __addon__.getAddonInfo('path')


def main():
    apiclient = AppApiClient.getDefaultClient()
    apiclient._log.setLevel(logging.DEBUG)

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
    cache = StvList(iuid, apiclient)

    try:
        cache.load(os.path.join(__cwd__, 'resources', 'cache.dat'))
    except:
        # first time
        xbmc.log('CACHE restore failed. If this is your first run, its ok')

    cache.list()

    thread.start_new_thread(home_screen_fill, (apiclient, cache))

    host = __addon__.getSetting('ADDON_SVC_HOST')
    port = int(__addon__.getSetting('ADDON_SVC_PORT'))

    addon_service = AddonService(host, port, apiclient)
    scrobbler = Scrobbler(cache)
    rpc_listener = RPCListenerHandler(cache)

    apiclient.start()
    addon_service.start()
    scrobbler.start()
    rpc_listener.start()

    xbmc.log('Entering service loop')
    while True:
        time.sleep(0.5)

        if not rpc_listener.isAlive() and not scrobbler.isAlive() and not addon_service.isAlive():
            xbmc.log('Service loop end. Both threads are dead')
            break

        if False and xbmc.abortRequested:
            xbmc.log('service.py abortRequested')
            break;

    xbmc.log('library and scrobbler quit')
    cache.save(os.path.join(__cwd__, 'resources', 'cache.dat'))


if __name__ == "__main__":
    main()
