# -*- coding: utf-8 -*- 
"""
Default file for SynopsiTV addon. See addon.xml 
<extension point="xbmc.python.pluginsource" library="addon.py">
"""
# xbmc
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

# python standart lib
import urllib
import sys
import os
import time
import json
import urllib2
import re
import os.path
import logging
import traceback
import subprocess
from datetime import datetime
import CommonFunctions

# application
from app_apiclient import AppApiClient, LoginState, AuthenticationError
from utilities import *
from cache import StvList
from xbmcrpc import xbmc_rpc

__addon__  = get_current_addon()
__addonname__ = __addon__.getAddonInfo('name')
__cwd__	= __addon__.getAddonInfo('path')
__author__  = __addon__.getAddonInfo('author')
__version__   = __addon__.getAddonInfo('version')

log('SYS ARGV:' + str(sys.argv)) 

url_parsed = urlparse.urlparse(sys.argv[2])
params = urlparse.parse_qs(url_parsed.query)

# log('url_parsed:' + str(url_parsed))
log('params:' + str(params))

check_first_run()

apiClient = AppApiClient.getDefaultClient()
apiClient.login_state_announce = LoginState.AddonDialog
stvList = StvList.getDefaultList(apiClient)

# log(str(sys.argv))

param_vars = ['url', 'name', 'mode', 'type', 'data', 'stv_id']
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
   

dirhandle = int(sys.argv[1])

log('mode: %s type: %s' % (p['mode'], p['type']))	
log('url: %s' % (p['url']))  
log('data: %s' % (p['data']))	

if p['mode']==None:
	show_categories()
	xbmcplugin.endOfDirectory(dirhandle)

elif p['mode'] in [ActionCode.MovieRecco, ActionCode.TVShows, ActionCode.LocalMovieRecco, ActionCode.TVShowEpisodes]:
	params = {'stv_id': p['stv_id']} if p['stv_id'] else {}
	try:
		show_submenu(p['mode'], dirhandle, **params)
	except:
		dialog_ok(t_nolocalrecco)
		xbmc.executebuiltin('Container.Update(plugin://plugin.video.synopsi, replace)')

elif p['mode']==ActionCode.UnwatchedEpisodes:
	try:
		show_submenu(p['mode'], dirhandle)
	except ListEmptyException:
		dialog_ok(t_nounwatched)
		xbmc.executebuiltin('Container.Update(plugin://plugin.video.synopsi, replace)')

elif p['mode']==ActionCode.UpcomingEpisodes:
	try:
		show_submenu(p['mode'], dirhandle)
	except ListEmptyException:
		dialog_ok(t_noupcoming)
		xbmc.executebuiltin('Container.Update(plugin://plugin.video.synopsi, replace)')
		
elif p['mode']==ActionCode.VideoDialogShow:
	show_video_dialog(p['json_data'])

elif p['mode']==ActionCode.VideoDialogShowById:
	try:
		stv_id = int(p['stv_id'])
	except TypeError:
		log('ERROR / Wrong params')
		sys.exit(0)

	show_video_dialog_byId(stv_id)

elif p['mode']==ActionCode.LoginAndSettings:
	__addon__.openSettings()

elif p['mode']==970:
	xbmc.executebuiltin('CleanLibrary(video)')
	xbmc.executebuiltin('UpdateLibrary(video)')

elif p['mode']==971:
	stvList.list()	
	
elif p['mode']==972:
	search = apiClient.search('Code')
	data = { 'movies': search['search_result']}
	open_select_movie_dialog(data)   
	

elif p['mode']==999:
	xbmcplugin.endOfDirectory(dirhandle)
	jdata = {
		'id': 1232,
		'name': 'XBMC Skinning Tutorial',
		'plot': 'Lorem Ipsum je fiktívny text, používaný pri návrhu tlačovín a typografie. Lorem Ipsum je štandardným výplňovým textom už od 16. storočia, keď neznámy tlačiar zobral sadzobnicu plnú tlačových znakov a pomiešal ich, aby tak vytvoril vzorkovú knihu. Prežil nielen päť storočí, ale aj skok do elektronickej sadzby, a pritom zostal v podstate nezmenený. Spopularizovaný bol v 60-tych rokoch 20.storočia, vydaním hárkov Letraset, ktoré obsahovali pasáže Lorem Ipsum, a neskôr aj publikačným softvérom ako Aldus PageMaker, ktorý obsahoval verzie Lorem Ipsum. Lorem Ipsum je fiktívny text, používaný pri návrhu tlačovín a typografie. Lorem Ipsum je štandardným výplňovým textom už od 16. storočia, keď neznámy tlačiar zobral sadzobnicu plnú tlačových znakov a pomiešal ich, aby tak vytvoril vzorkovú knihu. Prežil nielen päť storočí, ale aj skok do elektronickej sadzby, a pritom zostal v podstate nezmenený. Spopularizovaný bol v 60-tych rokoch 20.storočia, vydaním hárkov Letraset, ktoré obsahovali pasáže Lorem Ipsum, a neskôr aj publikačným softvérom ako Aldus PageMaker, ktorý obsahoval verzie Lorem Ipsum.',
		'cover_large': 'https://s3.amazonaws.com/titles.synopsi.tv/01498059-267.jpg',
		'xbmc_movie_detail': {
			'director': 'Ratan Hatan',
			'writer': 'Eugo Aianora',
			'runtime': '102',
			'premiered': '1. aug. 2012',
		}
	}
	show_video_dialog(jdata)
	
