# -*- coding: utf-8 -*- 
"""
Default file for SynopsiTV addon. See addon.xml 
<extension point="xbmc.python.pluginsource" library="addon.py">
"""
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmcvfs
import urllib
import sys
import os
import time
import json
import urllib2
import re
import os.path
import logging
import socket
from datetime import datetime
import test
from app_apiclient import AppApiClient, LoginState, AuthenticationError
from utilities import *
from cache import StvList

class AddonClient():
    def __init__(self, pluginhandle):        
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.pluginhandle = pluginhandle

    def execute(command, **arguments):
        json = { 
            'command': command,
            'pluginhandle': self.pluginhandle,
            'data': **arguments
        }

        xbmc.log(json)

        self.s.connect(('localhost', 9889))
        self.sendall(json.dumps(json))
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

    if p['mode']==None or p['url']==None or len(p['url'])<1:
        addonClient.execute('show_categories')
    elif p['mode']==1:
        addonClient.execute(
            'show_movies'
            {
                'url': p['url'],
                'type': p['type'],
                'movie_type': 'movie'
            }
        )
    elif p['mode']==11:
        addonClient.execute(
            'show_movies'
            {
                'url': p['url'],
                'type': p['type'],
                'movie_type': 'episode'
            }
        )
    elif p['mode']==12:
        addonClient.execute(
            'show_movies'
            {
                'url': p['url'],
                'type': p['type'],
                'movie_type': 'movie'
            }
        )
    elif p['mode']==13:
            addonClient.execute(
            'show_movies'
            {
                'url': p['url'],
                'type': p['type'],
                'movie_type': 'episode'
            }
        )
    elif p['mode']==20:
        addonClient.execute(
            'show_movies'
            {
                'url': p['url'],
                'type': p['type'],
                'movie_type': 'none'
            }
        )
    elif p['mode']==2:
        p['json_data']['type'] = p['type']
        addonClient.execute(
            'show_video_dialog'
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

        


