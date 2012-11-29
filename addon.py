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
from utilities import *
from cache import StvList
from xbmcrpc import xbmc_rpc
from addonutilities import *

class AddonClient(object):
	def __init__(self, pluginhandle):		
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.pluginhandle = pluginhandle

	def execute(self, command, **arguments):
		json_data = { 
			'command': command,
			'arguments': arguments
		}

		self.s.connect(('localhost', 9190))
		xbmc.log('CLIENT / SEND / ' + dump(json_data))
		self.s.sendall(json.dumps(json_data))
		response = self.s.recv(16384)
		#~ xbmc.log('CLIENT / RAW RESPONSE / ' + response)
		self.s.close()		
		response_json = json.loads(response)
		#~ xbmc.log('CLIENT / JSON RESPONSE / ' + dump(response))
		return response_json

	def get_global_recco(self, movie_type):
		return self.execute('get_global_recco', movie_type=movie_type)

	def get_tvshows(self):
		return self.execute('get_tvshows')

	def get_local_recco2(self, movie_type):
		return self.execute('get_local_recco2', movie_type=movie_type)

	def get_upcoming_episodes(self):
		return self.execute('get_upcoming_episodes')
		
	def get_unwatched_episodes(self):			
		return self.execute('get_unwatched_episodes')

	def get_tvshow_season(self, tvshow_id):			
		return self.execute('get_tvshow_season', tvshow_id=tvshow_id)
		
	def get_title(self, stv_id, **kwargs):
		return self.execute('get_title', stv_id=stv_id, **kwargs)

	def get_title_similars(self, stv_id):
		return self.execute('get_title_similars', stv_id=stv_id)
		
	def get_tvshow(self, tvshow_id):
		return self.execute('get_title', tvshow_id=tvshow_id)

	def cache_getByStvId(self, stv_id):
		return self.execute('cache_getByStvId', stv_id=stv_id)

	def show_video_dialog(self, json_data):
		return self.execute('show_video_dialog', json_data=json_data)

	def show_video_dialog_byId(self, stv_id):
		return self.execute('show_video_dialog_byId', stv_id=stv_id)

def get_item_list(action_code, **kwargs):
	log('get_item_list:' + str(action_code))
	
	if action_code==ActionCode.MovieRecco:
		return addonclient.get_global_recco('movie')['titles']
	elif action_code==ActionCode.TVShows:
		return addonclient.get_tvshows()
	elif action_code==ActionCode.LocalMovieRecco:
		return addonclient.get_local_recco2('movie')
	elif action_code==ActionCode.UnwatchedEpisodes:
		return addonclient.get_unwatched_episodes()
	elif action_code==ActionCode.UpcomingEpisodes:
		return addonclient.get_upcoming_episodes()
	elif action_code==ActionCode.TVShowEpisodes:
		return addonclient.get_tvshow_season(kwargs['stv_id'])

def show_submenu(action_code, dirhandle, **kwargs):
	try:
		item_list = get_item_list(action_code, **kwargs)
		show_movie_list(item_list, dirhandle)
	except ListEmptyException:	
		raise
	except:
		log(traceback.format_exc())
		dialog_ok(t_listing_failed)
		xbmc.executebuiltin('Container.Update(plugin://plugin.video.synopsi, replace)')		 



                                                                                                                                                                                                            
#~ def show_video_dialog_byId(stv_id):
	#~ stv_details = addonclient.get_title(stv_id, defaultDetailProps, defaultCastProps)
	#~ show_video_dialog_data(stv_details)

#~ def show_video_dialog(json_data):
	#~ # log('show video:' + dump(json_data))
#~ 
	#~ if json_data.get('type') == 'tvshow':
		#~ stv_details = addonclient.get_tvshow(json_data['id'], cast_props=defaultCastProps)
	#~ else:	show_video_dialog(p['json_data'])
		#~ stv_details = addonclient.get_title(json_data['id'])
#~ 
	#~ show_video_dialog_data(stv_details, json_data)

#~ def show_video_dialog_data(stv_details, json_data={}):
#~ 
	#~ # add xbmc id if available
	#~ if json_data.has_key('id'):
		#~ cacheItem = addonclient.cache_getByStvId(json_data['id'])
		#~ if cacheItem:
			#~ json_data['xbmc_id'] = cacheItem['id']
			#~ json_data['xbmc_movie_detail'] = xbmc_rpc.get_details('movie', json_data['xbmc_id'], True)
#~ 
	#~ # add similars or seasons (bottom covers list)
	#~ if stv_details['type'] == 'movie':
		#~ # get similar movies
		#~ t1_similars = addonclient.get_title_similars(stv_details['id'])
		#~ if t1_similars.has_key('titles'):
			#~ stv_details['similars'] = t1_similars['titles']			
	#~ elif stv_details['type'] == 'tvshow':
		#~ # append seasons
		#~ if stv_details.has_key('seasons'):
			#~ stv_details['similars'] = [ {'id': i['id'], 'name': 'Season %d' % i['season_number'], 'cover_medium': i['cover_medium']} for i in stv_details['seasons'] ]
#~ 
	#~ tpl_data = video_dialog_template_fill(stv_details, json_data)
	#~ open_video_dialog(tpl_data)
		

__addon__  = get_current_addon()
__addonname__ = __addon__.getAddonInfo('name')
__cwd__	= __addon__.getAddonInfo('path')
__author__  = __addon__.getAddonInfo('author')
__version__   = __addon__.getAddonInfo('version')
dirhandle = int(sys.argv[1])

log('SYS ARGV:' + str(sys.argv)) 

url_parsed = urlparse.urlparse(sys.argv[2])
params = urlparse.parse_qs(url_parsed.query)

check_first_run()

stvList = StvList.getDefaultList(apiClient)
addonclient = AddonClient(dirhandle)

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

#~ log('params:' + str(params))   
#~ log('mode: %s type: %s' % (p['mode'], p['type']))	
#~ log('url: %s' % (p['url']))  
#~ log('data: %s' % (p['data']))	

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
	addonclient.show_video_dialog(p['json_data'])

elif p['mode']==ActionCode.VideoDialogShowById:
	try:
		stv_id = int(p['stv_id'])
	except TypeError:
		log('ERROR / Wrong params')
		sys.exit(0)

	addonclient.show_video_dialog_byId(stv_id)

elif p['mode']==ActionCode.LoginAndSettings:
	__addon__.openSettings()

# debugging
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
	
