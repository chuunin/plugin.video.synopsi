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
import test
from app_apiclient import AppApiClient, LoginState, AuthenticationError
from utilities import *
from cache import StvList
from xbmcrpc import xbmc_rpc


common = CommonFunctions
common.plugin = "SynopsiTV"

# test files
movies = test.jsfile
movie_response = { 'titles': movies }

class ActionCode:
	MovieRecco = 10
	TVShows = 20
	LocalMovieRecco = 30
	UnwatchedEpisodes = 40
	UpcomingEpisodes = 50

	LoginAndSettings = 90

	TVShowEpisodes = 60
	
	VideoDialogShow = 900
	VideoDialogShowById = 910



def log(msg):
	#logging.debug('ADDON: ' + str(msg))
	xbmc.log('ADDON / ' + str(msg))

def uniquote(s):
	return urllib.quote_plus(s.encode('ascii', 'backslashreplace'))

def uniunquote(uni):
	return urllib.unquote_plus(uni.decode('utf-8'))

class ListEmptyException(BaseException):
	pass

def get_local_recco(movie_type):
	resRecco =  apiClient.profileRecco(movie_type, True, reccoDefaulLimit, reccoDefaultProps)

	# log('local recco for ' + movie_type)
	# for title in resRecco['titles']:
	#	log('resRecco:' + title['name'])

	return resRecco

def get_local_recco2(movie_type):
	""" Updates the get_local_recco function result to include stv_title_hash """
	recco = get_local_recco(movie_type)['titles']
	
	for title in recco:
		if stvList.hasStvId(title['id']):
			cached_title = stvList.getByStvId(title['id'])
			log(dump(cached_title))
			title['stv_title_hash'] = cached_title['stv_title_hash']
			title['file'] = cached_title['file']
			
	stvList.list()
	
		
	return recco	


def get_global_recco(movie_type):
	resRecco =  apiClient.profileRecco(movie_type, False, reccoDefaulLimit, reccoDefaultProps)

	# log('global recco for ' + movie_type)
	# for title in resRecco['titles']:
	#	log(title['name'])

	return resRecco


def get_unwatched_episodes():
	episodes =  apiClient.unwatchedEpisodes()

	# log('unwatched episodes')
	# for title in episodes['lineup']:
	#	 log(title['name'])

	result = episodes['lineup']
	return result
	
def get_upcoming_episodes():
	episodes =  apiClient.unwatchedEpisodes()

	# log('upcoming episodes')
	# for title in episodes['upcoming']:
	#	 log(title['name'])

	result = episodes['upcoming']
	return result

def get_top_tvshows():
	episodes = apiClient.unwatchedEpisodes()

	# log('top tvshows')
	# for title in episodes['top']:
	#	 log(title['name'])

	result = episodes['top']
	return result

def get_tvshows():
	local_tvshows = stvList.getAllByType('tvshow')
	log('local_tvshows: ' + str(local_tvshows))
	result = []
	result += local_tvshows.values()
	result += get_top_tvshows()

	return result

def get_local_tvshows():
	localtvshows = xbmc_rpc.get_all_tvshows()
	log(dump(localtvshows))

	return [ { 'name': item['label'], 'cover_medium': item['thumbnail'] } for item in localtvshows['tvshows'] ]

def get_tvshow_season(tvshow_id):
	season = apiClient.season(tvshow_id)
	return season['episodes']

def get_lists():
	log('get_lists')
	return movies


def get_movies_in_list(listid):
	log('get_movies_in_list')
	return movies


def get_trending_movies():
	log('get_trending_movies')
	return movies


def get_trending_tvshows():
	log('get_trending_tvshows')
	return movies

def get_item_list(action_code, **kwargs):
	log('get_item_list:' + str(action_code))
	
	if action_code==ActionCode.MovieRecco:
		return get_global_recco('movie')['titles']
	elif action_code==ActionCode.TVShows:
		return get_tvshows()
	elif action_code==ActionCode.LocalMovieRecco:
		return get_local_recco2('movie')
	elif action_code==ActionCode.UnwatchedEpisodes:
		return get_unwatched_episodes()
	elif action_code==ActionCode.UpcomingEpisodes:
		return get_upcoming_episodes()
	elif action_code==ActionCode.TVShowEpisodes:
		return get_tvshow_season(kwargs['stv_id'])


def add_to_list(movieid, listid):
	pass

def set_already_watched(stv_id, rating):
	log('already watched %d rating %d' % (stv_id, rating))
	apiClient.titleWatched(stv_id, rating=rating)

class VideoDialog(xbmcgui.WindowXMLDialog):
	"""
	Dialog about video information.
	"""
	def __init__(self, *args, **kwargs):
		self.data = kwargs['data']
		self.controlId = None

	def onInit(self):
		win = xbmcgui.Window(xbmcgui.getCurrentWindowDialogId())
		win.setProperty("Movie.Title", self.data["name"])
		win.setProperty("Movie.Plot", self.data["plot"])
		win.setProperty("Movie.Cover", self.data["cover_full"])
		# win.setProperty("Movie.Cover", "default.png")

		for i in range(5):
			win.setProperty("Movie.Similar.{0}.Cover".format(i + 1), "default.png")
	   
		# set available labels
		i = 1
		for key, value in self.data['labels'].iteritems():
			win.setProperty("Movie.Label.{0}.1".format(i), key)
			win.setProperty("Movie.Label.{0}.2".format(i), value)
			i = i + 1

		# enable file playing if available
		if self.data.has_key('file'):
			win.setProperty("Movie.File", self.data['file'])
			self.getControl(5).setEnabled(True)

		win.setProperty('BottomListingLabel', self.data['BottomListingLabel'])

		# similars
		items = []

		if self.data.has_key('similars'):
			for item in self.data['similars']:
				li = xbmcgui.ListItem(item['name'], iconImage=item['cover_medium'])
				li.setProperty('id', str(item['id']))
				items.append(li)

			# similars alternative
			self.getControl(59).addItems(items)

		tmpTrail = self.data.get('trailer')
		if tmpTrail:
			_youid = tmpTrail.split("/")
			_youid.reverse()
			win.setProperty("Movie.Trailer.Id", str(_youid[0]))
		else:
			self.getControl(10).setEnabled(False)

		if not self.data['type'] in ['movie', 'episode']:
			self.getControl(11).setEnabled(False)

	def onClick(self, controlId):
		log('onClick: ' + str(controlId))
		if controlId == 5: # play
			self.close()
		elif controlId == 6: # add to list
			dialog = xbmcgui.Dialog()
			ret = dialog.select('Choose list', ['Watch later', 'Action', 'Favorite'])
		elif controlId == 10: # trailer
			self.close()
		elif controlId == 11: # already watched
			rating = get_rating()
			if rating < 4:
				set_already_watched(self.data['id'], rating)
			self.close()
			xbmc.executebuiltin('Container.Refresh()')
		elif controlId == 59:
			selected_item = self.getControl(59).getSelectedItem()
			stv_id = int(selected_item.getProperty('id'))

			if self.data['type'] == 'tvshow':
				self.close()
				xbmc.executebuiltin('Container.Update(plugin://plugin.video.synopsi/addon.py?mode=%d&amp;stv_id=%d)' % (ActionCode.TVShowEpisodes, stv_id))
			else:
				show_video_dialog_byId(stv_id)
		elif controlId == 13:
			new_identity = user_title_search()
			if new_identity and self.data.has_key('id') and self.data.get('type') not in ['tvshow', 'season']:
				apiClient.title_identify_correct(new_identity['id'], self.data['stv_title_hash'])


	def onFocus(self, controlId):
		self.controlId = controlId

	def onAction(self, action):
		log('action: %s focused id: %s' % (str(action.getId()), str(self.controlId)))		
		if (action.getId() in CANCEL_DIALOG):
			self.close()


def add_directory(name, url, mode, iconimage, atype):
	u = sys.argv[0]+"?url="+uniquote(url)+"&mode="+str(mode)+"&name="+uniquote(name)+"&type="+str(atype)
	ok = True
	liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
	# liz.setInfo(type="Video", infoLabels={"Title": name} )
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
	return ok


def add_movie(movie, url, mode, iconimage, movieid):
	json_data = dump(movie)
	u = sys.argv[0]+"?url="+uniquote(url)+"&mode="+str(mode)+"&name="+uniquote(movie.get('name'))+"&data="+uniquote(json_data)
	li = xbmcgui.ListItem(movie.get('name'), iconImage="DefaultFolder.png", thumbnailImage=iconimage)
	if movie.get('watched'):
		li.setInfo( type="Video", infoLabels={ "playcount": 1 } )

	new_li = (u, li, False)

	return new_li

def show_categories():
	"""
	Shows initial categories on home screen.
	"""
	xbmc.executebuiltin("Container.SetViewMode(503)")
	add_directory("Movie Recommendations", "url", ActionCode.MovieRecco, "list.png", 1)
	add_directory("TV Shows", "url", ActionCode.TVShows, "list.png", 1)
	add_directory("Local Movie recommendations", "url", ActionCode.LocalMovieRecco, "list.png", 2)
	add_directory("Unwatched TV Show Episodes", "url", ActionCode.UnwatchedEpisodes, "icon.png", 3)
	add_directory("Upcoming TV Episodes", "url", ActionCode.UpcomingEpisodes, "icon.png", 33)
	add_directory("Login and Settings", "url", ActionCode.LoginAndSettings, "icon.png", 1)

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

def show_movie_list(item_list, dirhandle):
	errorMsg = None
	try:
		if not item_list:
			raise ListEmptyException
		
		lis = []	
		for movie in item_list:
			# log(dump(movie))
			lis.append(
				add_movie(movie, "url", ActionCode.VideoDialogShow, movie.get('cover_medium'), movie.get("id"))
			)

		xbmcplugin.addDirectoryItems(dirhandle, lis)

	except AuthenticationError:
		errorMsg = True
	finally:
		xbmcplugin.endOfDirectory(dirhandle)
		xbmc.executebuiltin("Container.SetViewMode(500)")

	if errorMsg:
		if dialog_check_login_correct():
			xbmc.executebuiltin('Container.Refresh')
		else:
			xbmc.executebuiltin('Container.Update(plugin://plugin.video.synopsi, replace)')		 
  
	# xbmc.executebuiltin('Container.Update(plugin://plugin.video.synopsi?url=url&mode=999)')


def show_video_dialog_byId(stv_id):
	stv_details = apiClient.title(stv_id, detailProps, defaultCastProps)
	show_video_dialog_data(stv_details)

def show_video_dialog(json_data):
	# log('show video:' + dump(json_data))

	if json_data.get('type') == 'tvshow':
		stv_details = apiClient.tvshow(json_data['id'], cast_props=defaultCastProps)
	else:
		stv_details = apiClient.title(json_data['id'], detailProps, defaultCastProps)

	show_video_dialog_data(stv_details, json_data)

def show_video_dialog_data(stv_details, json_data={}):
	# add xbmc id if available
	if json_data.has_key('id') and stvList.hasStvId(json_data['id']):
		cacheItem = stvList.getByStvId(json_data['id'])
		json_data['xbmc_id'] = cacheItem['id']
		log('xbmc id:' + str(json_data['xbmc_id']))
		json_data['xbmc_movie_detail'] = xbmc_rpc.get_details('movie', json_data['xbmc_id'], True)

	log('show video:' + dump(json_data))
	log('stv_details video:' + dump(stv_details))
	
	# update empty stv_details with only nonempty values from xbmc
	for k, v in json_data.iteritems():
		if v and not stv_details.get(k):
			stv_details[k] = v

	tpl_data=stv_details
	 
	stv_labels = {}		
	if tpl_data.get('directors'): 
		stv_labels['Director'] = ', '.join(tpl_data['directors'])
	if tpl_data.get('cast'):	
		stv_labels['Cast'] = ', '.join(map(lambda x:x['name'], tpl_data['cast']))
	if tpl_data.get('runtime'):
		stv_labels['Runtime'] = '%d min' % tpl_data['runtime']
	if tpl_data.get('date'):
		stv_labels['Release date'] = datetime.fromtimestamp(tpl_data['date']).strftime('%x')

	xbmclabels = {}
	if tpl_data.has_key('xbmc_movie_detail'):
		d = tpl_data['xbmc_movie_detail']
		if d.get('director'):
			xbmclabels["Director"] = ', '.join(d['director'])
		if d.get('writer'):
			xbmclabels["Writer"] = ', '.join(d['writer'])
		if d.get('runtime'):
			xbmclabels["Runtime"] = d['runtime'] + ' min'
		if d.get('premiered'):	
			xbmclabels["Release date"] = d['premiered']
		if d.get('file'):
			tpl_data['file'] = d.get('file')

	labels = {}
	labels.update(xbmclabels)
	labels.update(stv_labels)
	
	# set unavail labels
	for label in ['Director','Cast','Runtime','Release date']:
		if not labels.has_key(label):
			labels[label] = t_unavail

	tpl_data['labels'] = labels
	tpl_data['BottomListingLabel'] = type2listinglabel.get(tpl_data['type'], '')	

	if tpl_data['type'] == 'movie':
		# get similar movies
		similars = apiClient.titleSimilar(tpl_data['id'])
		if similars.has_key('titles'):
			tpl_data['similars'] = similars['titles']
	elif tpl_data['type'] == 'tvshow':
		# append seasons
		if tpl_data.has_key('seasons'):
			tpl_data['similars'] = [ {'id': i['id'], 'name': 'Season %d' % i['season_number'], 'cover_medium': i['cover_medium']} for i in stv_details['seasons'] ]

	open_video_dialog(tpl_data)

def open_video_dialog(tpl_data):
	try:
		win = xbmcgui.Window(xbmcgui.getCurrentWindowDialogId())
	except ValueError, e:
		ui = VideoDialog("VideoInfo.xml", __cwd__, "Default", data=tpl_data)
		ui.doModal()
		del ui
	else:
		win = xbmcgui.WindowDialog(xbmcgui.getCurrentWindowDialogId())
		win.close()
		ui = VideoDialog("VideoInfo.xml", __cwd__, "Default", data=tpl_data)
		ui.doModal()
		del ui

class SelectMovieDialog(xbmcgui.WindowXMLDialog):
	""" Dialog for choosing movie corrections """
	def __init__(self, *args, **kwargs):
		self.data = kwargs['data']
		self.controlId = None
		self.selectedMovie = None

	def onInit(self):
		items = []
		for item in self.data['movies']:
			text = '%s (%d) %s' % (item['name'], item['year'], ', '.join(item['directors']))
			li = xbmcgui.ListItem(text, iconImage=item['cover_medium'])
			li.setProperty('id', str(item['id']))
			items.append(li)

			self.getControl(59).addItems(items)

	def onClick(self, controlId):
		log('onClick: ' + str(controlId))
		if self.controlId == 59:
			sel_index = self.getControl(59).getSelectedPosition()
			self.selectedMovie = self.data['movies'][sel_index]
			self.close()


	def onFocus(self, controlId):
		self.controlId = controlId

	def onAction(self, action):
		log('action: %s focused id: %s' % (str(action.getId()), str(self.controlId)))
		if (action.getId() in CANCEL_DIALOG):
			self.close()

def open_select_movie_dialog(tpl_data):
	ui = SelectMovieDialog("SelectMovie.xml", __cwd__, "Default", data=tpl_data)
	ui.doModal()
	result = ui.selectedMovie
	del ui
	return result


def user_title_search():
	search_term = common.getUserInput("Title", "")
	if search_term:
		results = apiClient.search(search_term)
		if len(results['search_result']) == 0:
			dialog_ok('No results')
		else:
			data = { 'movies': results['search_result'] }
			return open_select_movie_dialog(data)
	else:
		dialog_ok('Enter a title name to search for')

	return
