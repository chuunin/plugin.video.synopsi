"""
This is default file of SynopsiTV service. See addon.xml
<extension point="xbmc.service" library="service.py" start="login|startup">
"""
from scrobbler import Scrobbler
from library import RPCListenerHandler
from cache import *
import xbmc, xbmcgui, xbmcaddon
import apiclient

__addon__  = xbmcaddon.Addon()

def main():

    # try to restore cache  
    cacheSer = __addon__.getSetting(id='CACHE')
    
    # get or generate install-unique ID
    iuid = __addon__.getSetting(id='INSTALL_UID')
    if not iuid:
        iuid = generate_iuid()
        xbmc.log('iuid:' + iuid)
        __addon__.setSetting(id='INSTALL_UID', value=iuid)

    apiclient1 = apiclient.apiclient(
        __addon__.getSetting('BASE_URL'),
        __addon__.getSetting('KEY'),
        __addon__.getSetting('SECRET'),
        __addon__.getSetting('USER'),
        __addon__.getSetting('PASS'),
    )

# once per library methods change, to reinit the serialzed object
#   cacheSer = ''   
# test string
#   cacheSer = 'KGxwMAooZHAxClMnbW92aWUtLTgnCnAyCihkcDMKVm1vdmllaWQKcDQKSTgKc1ZsYXN0cGxheWVkCnA1ClYyMDEyLTEwLTA1IDExOjEyOjU0CnA2CnNWbGFiZWwKcDcKVkEgVmVyeSBIYXJvbGQgJiBLdW1hciBDaHJpc3RtYXMKcDgKc1ZpbWRibnVtYmVyCnA5ClZ0dDEyNjg3OTkKcDEwCnNTJ3N0dl9oYXNoJwpwMTEKUycxNTk3OWNmYWRjOWFkMjY0ZmE5YjI5YmU3ZmQwNTgzZDI5MDBjYjUwJwpwMTIKc1ZmaWxlCnAxMwpWL1VzZXJzL3NtaWQvTW92aWVzL01vdmllcy9BIFZlcnkgSGFyb2xkIEFuZCBLdW1hciBDaHJpc3RtYXMgRFZEUmlwIFh2aUQtRGlBTU9ORC9kbWQtdmhha2MuYXZpCnAxNApzVnBsYXljb3VudApwMTUKSTIKc1MndHlwZScKcDE2ClZtb3ZpZQpwMTcKc1MnaWQnCnAxOApJOApzc2EoZHAxOQpnMTQKZzMKc2EoZHAyMAphLg=='
    cache = StvList(iuid, apiclient1)
 
    try:
        cache.deserialize(cacheSer)
    except:
        # first time
        xbmc.log('CACHE restore failed. If this is your first run, its ok')

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


    __addon__.setSetting(id='CACHE', value=cache.serialize())


if __name__ == "__main__":
    main()
