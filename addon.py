# -*- coding: utf-8 -*- 
"""
Default file for SynopsiTV addon. See addon.xml 
<extension point="xbmc.python.pluginsource" library="addon.py">
"""
import urlparse
import socket
import json
from utilities import get_current_addon
from addon_utilities import uniunquote

def log(msg):
    #logging.debug('ADDON: ' + str(msg))
    xbmc.log('ADDON / ' + str(msg))

class AddonClient(object):
    def __init__(self, pluginhandle):        
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.pluginhandle = pluginhandle

    def execute(self, command, arguments={}):
        arguments['pluginhandle'] = self.pluginhandle
        json_data = { 
            'command': command,
            'arguments': arguments
        }

        self.s.connect(('localhost', 9889))
        xbmc.log('CLIENT / SEND / ' + json.dumps(json_data, indent=4))
        self.s.sendall(json.dumps(json_data))
        self.s.close()        


if __name__=='__main__':
    __addon__  = get_current_addon()

    __addonname__ = __addon__.getAddonInfo('name')
    __cwd__    = __addon__.getAddonInfo('path')
    __author__  = __addon__.getAddonInfo('author')
    __version__   = __addon__.getAddonInfo('version')
    addonClient = AddonClient(int(sys.argv[1]))

    xbmc.log('SYS ARGV:' + str(sys.argv)) 

    url_parsed = urlparse.urlparse(sys.argv[2])
    params = urlparse.parse_qs(url_parsed.query)

    xbmc.log('url_parsed:' + str(url_parsed))
    xbmc.log('params:' + str(params))

    param_vars = ['url', 'name', 'mode', 'type', 'data']
    p = dict([(k, params.get(k, [None])[0]) for k in param_vars])

    if p['url']:
        p['url']=uniunquote(p['url'])

    if p['name']:
        p['name']=uniunquote(p['name'])

    if p['mode']:
        p['mode']=int(p['mode'])

    if p['type']:
        p['type']=int(p['type'])

    if p['data']:
        p['data'] = uniunquote(p['data'])
        p['json_data'] = json.loads(p['data'])

    log('mode: %s type: %s' % (p['mode'], p['type']))    
    log('mode type: %s' % type(p['mode']))   
    log('url: %s' % (p['url']))  
    log('data: %s' % (p['data']))    

    if p['mode']==None or len(p['url'])<1:
        addonClient.execute('show_categories')
    elif p['mode']==1:
        addonClient.execute(
            'show_movies',
            {
                'url': p['url'],
                'list_type': p['type'],
                'movie_type': 'movie'
            }
        )
    elif p['mode']==11:
        addonClient.execute(
            'show_movies',
            {
                'url': p['url'],
                'list_type': p['type'],
                'movie_type': 'episode'
            }
        )
    elif p['mode']==12:
        addonClient.execute(
            'show_movies',
            {
                'url': p['url'],
                'list_type': p['type'],
                'movie_type': 'movie'
            }
        )
    elif p['mode']==13:
            addonClient.execute(
            'show_movies',
            {
                'url': p['url'],
                'list_type': p['type'],
                'movie_type': 'episode'
            }
        )
    elif p['mode']==20:
        addonClient.execute(
            'show_movies',
            {
                'url': p['url'],
                'list_type': p['type'],
                'movie_type': 'none'
            }
        )
    elif p['mode']==2:
        p['json_data']['type'] = p['type']
        addonClient.execute(
            'show_video_dialog',
            {
                'url': p['url'],
                'name': p['name'],
                'data': p['json_data']
            }
        )
    elif p['mode']==90:
        addonClient.execute(
            'addon_openSettings'
        )
    elif p['mode']==999:
        addonClient.execute(
            'test_dialogwindow'
        )

        


