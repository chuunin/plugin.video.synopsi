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
import test
from app_apiclient import AppApiClient
from utilities import *
from cache import StvList

# from PIL import Image, ImageDraw, ImageOps

movies = test.jsfile
movie_response = { 'titles': movies }

__addon__  = xbmcaddon.Addon()
addonPath = __addon__.getAddonInfo('path')

# xbmc.log(str(dir(xbmcvfs)))

def log(msg):
    #logging.debug('ADDON: ' + str(msg))
    xbmc.log('ADDON / ' + str(msg))

def get_local_recco(movie_type):
    global apiClient

    props = [ 'id', 'cover_full', 'cover_large', 'cover_medium', 'cover_small', 'cover_thumbnail', 'date',
    'genres', 'image', 'link', 'name', 'plot', 'released', 'trailer', 'type', 'year' ]

    resRecco =  apiClient.profileRecco(movie_type, True, props)

    log('local recco for ' + movie_type)

    # for title in resRecco['titles']:
    #     log('resRecco:' + title['name'])

    return resRecco


def get_global_recco(movie_type):
    global apiClient

    props = [ 'id', 'cover_full', 'cover_large', 'cover_medium', 'cover_small', 'cover_thumbnail', 'date',
    'genres', 'image', 'link', 'name', 'plot', 'released', 'trailer', 'type', 'year' ]

    resRecco =  apiClient.profileRecco(movie_type, False, props)

    log('global recco for ' + movie_type)

    # for title in resRecco['titles']:
    #     log(title['name'])

    return resRecco


def get_unwatched_episodes():
    global apiClient

    episodes =  apiClient.unwatchedEpisodes()

    log('unwatched episodes')
    for title in episodes['top']:
        log(title['name'])

    result = episodes['lineup']
    if not result:
        # let user know there is no lineup
        # provide some alternative listing
        result = episodes['upcoming']
        if not result:
            # let user know there is no upcoming
            # provide some alternative listing
            result = episodes['top']
        
    return result

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


def get_items(_type, movie_type = None):
    log('get_items:' + str(_type))
    try:
        if _type == 1:
            return get_global_recco(movie_type)['titles']
        elif _type == 2:
            return get_local_recco(movie_type)['titles']
        elif _type == 3:
            return get_unwatched_episodes()
        elif _type == 4:
            return get_lists()
        elif _type == 5:
            return get_trending_movies()
        elif _type == 6:
            return get_trending_tvshows()
    except Exception as exc:
        # error getting items
        # display error dialog and log errors
        log('ERROR /' + str(exc))
        return []

def add_to_list(movieid, listid):
    pass


def set_already_watched(movieid):
    pass

class VideoDialog(xbmcgui.WindowXMLDialog):
    """
    Dialog about video information.
    """
    def __init__(self, *args, **kwargs):
        self.data = kwargs['data']

    def onInit(self):
        win = xbmcgui.Window(xbmcgui.getCurrentWindowDialogId())
        win.setProperty("Movie.Title", self.data["name"])
        win.setProperty("Movie.Plot", self.data["plot"])
        win.setProperty("Movie.Cover", self.data["cover_large"])
        # win.setProperty("Movie.Cover", "default.png")

        for i in range(5):
            win.setProperty("Movie.Similar.{0}.Cover".format(i + 1), "default.png")

        labels = dict()

        if self.data.has_key('xbmc_id'):
            log('xbmc id:' + str(self.data['xbmc_id']))
            xbmc_movie_detail = get_details('movie', self.data['xbmc_id'], True)

            labels["Director"] = xbmc_movie_detail['director']
            labels["Writer"] = xbmc_movie_detail['writer']
            labels["Runtime"] = xbmc_movie_detail['runtime']
            labels["Release date"] = xbmc_movie_detail['premiered']

        # set available labels
        i = 1
        for key in labels.keys():
            win.setProperty("Movie.Label.{0}.1".format(i), key)
            win.setProperty("Movie.Label.{0}.2".format(i), labels[key])
            i = i + 1


        # similars
        i = 1
        for item in self.data['similars']:
            win.setProperty("Movie.Similar.{0}.Label".format(i), item['name'])
            win.setProperty("Movie.Similar.{0}.Cover".format(i), item['cover_large'])
            i = i + 1

        if self.data["trailer"]:
            _youid = self.data["trailer"].split("/")
            _youid.reverse()
            win.setProperty("Movie.Trailer.Id", str(_youid[0]))
        else:
            self.getControl(10).setEnabled(False)

        self.getControl(5).setEnabled(False)

    def onClick(self, controlId):
        if controlId == 5: # play
            pass
        if controlId == 6: # add to list
            dialog = xbmcgui.Dialog()
            ret = dialog.select('Choose list', ['Watch later', 'Action', 'Favorite'])
        if controlId == 10: # trailer
            pass
        if controlId == 11: # already watched
            pass
        log('controlId: ' + str(controlId))
        self.close()

    def onFocus(self, controlId):
        self.controlId = controlId

    def onAction(self, action):
        if (action.getId() in CANCEL_DIALOG):
            self.close()


def add_directory(name, url, mode, iconimage, type, view_mode=500):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&type="+urllib.quote_plus(str(type))
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    # liz.setInfo(type="Video", infoLabels={"Title": name} )
    liz.setProperty("Fanart_Image", addonPath + 'fanart.jpg')
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
    xbmc.executebuiltin("Container.SetViewMode({0})".format(view_mode))
    return ok


def add_movie(movie, url, mode, iconimage, movieid, view_mode=500):
    json_data = json.dumps(movie)
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&type="+str(type)+"&name="+urllib.quote_plus(movie.get('name'))+"&data="+urllib.quote_plus(json_data)
    ok = True
    liz = xbmcgui.ListItem(movie.get('name'), iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": "Titulok" } )
    liz.setProperty("Fanart_Image", addonPath + 'fanart.jpg')
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
    xbmc.executebuiltin("Container.SetViewMode({0})".format(view_mode))
    return ok


def show_categories():
    """
    Shows initial categories on home screen.
    """
    add_directory("Movie recommendations", "url", 1, "list.png", 1)
    add_directory("TV Show recommendations", "url", 11, "list.png", 1)
    add_directory("Local Movie recommendations", "url", 12, "list.png", 2)
    add_directory("Local TV Show recommendations", "url", 13, "list.png", 2)
    add_directory("Unwatched TV episodes", "url", 1, "icon.png", 3)
    add_directory("Lists", "url", 1, "icon.png", 4)
    # add_directory("Trending Movies", "url", 1, "icon.png", 5, view_mode=500)
    # add_directory("Trending TV Shows", "url", 1, "icon.png", 6)


def show_movies(url, type, movie_type):
    for movie in get_items(type, movie_type):
        log(json.dumps(movie, indent=4))
        movie['type'] = movie_type
        add_movie(movie, "stack://C:\Users\Tommy\Videos\Movies\J Edgar.2011.DVDRip XviD-PADDO\CD1\paddo-jedgar-a.avi , \
         C:\Users\Tommy\Videos\Movies\J Edgar.2011.DVDRip XviD-PADDO\CD2\paddo-jedgar-b.avi",
            2, movie.get('cover_medium'), movie.get("id"))


def show_video_dialog(url, name, json_data):
    global stvList, apiClient

    # add xbmc id if available
    if stvList.hasStvId(json_data['id']):
        cacheItem = stvList.getByStvId(json_data['id'])
        json_data['xbmc_id'] = cacheItem['id']

    log('show video:' + json.dumps(json_data, indent=4))

    # get similar movies
    similars = apiClient.titleSimilar(json_data['id'])
    json_data['similars'] = similars['titles']

    try:
        win = xbmcgui.Window(xbmcgui.getCurrentWindowDialogId())
    except ValueError, e:
        ui = VideoDialog("VideoInfo.xml", __cwd__, "Default", data=json_data)
        ui.doModal()
        del ui
    else:
        win = xbmcgui.WindowDialog(xbmcgui.getCurrentWindowDialogId())
        win.close()
        ui = VideoDialog("VideoInfo.xml", __cwd__, "Default", data=json_data)
        ui.doModal()
        del ui


def get_params():
    param=[]
    paramstring=sys.argv[2]
    if len(paramstring)>=2:
        params=sys.argv[2]
        cleanedparams=params.replace('?','')
        if (params[len(params)-1]=='/'):
            params=params[0:len(params)-2]
        pairsofparams=cleanedparams.split('&')
        param={}
        for i in range(len(pairsofparams)):
            splitparams={}
            splitparams=pairsofparams[i].split('=')
            if (len(splitparams))==2:
                param[splitparams[0]]=splitparams[1]

    return param

__addon__     = xbmcaddon.Addon()
__addonname__ = __addon__.getAddonInfo('name')
__cwd__       = __addon__.getAddonInfo('path')
__author__    = __addon__.getAddonInfo('author')
__version__   = __addon__.getAddonInfo('version')

# print sys.argv

params = get_params()
url = None
name = None
mode = None
type = None
data = None


apiClient = AppApiClient.getDefaultClient()
stvList = StvList.getDefaultList(apiClient)

# xbmc.log(str(sys.argv))

try:
    url=urllib.unquote_plus(params["url"])
except:
    pass
try:
    name=urllib.unquote_plus(params["name"])
except:
    pass
try:
    mode=int(params["mode"])
except:
    pass
try:
    type=int(params["type"])
except:
    pass

try:
    data = urllib.unquote_plus(params["data"])
    json_data = json.loads(data)
except:
    pass
   

log('mode: %s type: %s' % (mode, type))    
log('url: %s' % (url))    
log('data: %s' % (data))    

if mode==None or url==None or len(url)<1:
    show_categories()
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    xbmcgui.Window(xbmcgui.getCurrentWindowId()).clearProperty("Fanart_Image")
    xbmcgui.Window(xbmcgui.getCurrentWindowId()).setProperty("Fanart_Image", addonPath + 'fanart.jpg')
    xbmcgui.Window(xbmcgui.getCurrentWindowId()).setProperty("Fanart", addonPath + 'fanart.jpg')

    xbmc.executebuiltin("Container.SetViewMode(503)")
elif mode==1:
    xbmc.log('movies')
    show_movies(url, type, 'movie')
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
elif mode==11:
    xbmc.log('tv shows')
    show_movies(url, type, 'episode')
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
elif mode==12:
    xbmc.log('movies local')
    show_movies(url, type, 'movie')
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
elif mode==13:
    xbmc.log('tv shows')
    show_movies(url, type, 'episode')
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
elif mode==2:
    json_data['type'] = type
    show_video_dialog(url, name, json_data)


