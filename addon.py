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
from datetime import datetime
import test
from app_apiclient import AppApiClient, LoginState, AuthenticationError
from utilities import *
from cache import StvList

# from PIL import Image, ImageDraw, ImageOps

movies = test.jsfile
movie_response = { 'titles': movies }

def log(msg):
    #logging.debug('ADDON: ' + str(msg))
    xbmc.log('ADDON / ' + str(msg))

def uniquote(s):
    return urllib.quote_plus(s.encode('ascii', 'backslashreplace'))

def uniunquote(uni):
    return urllib.unquote_plus(uni.decode('utf-8'))

def get_local_recco(movie_type):
    resRecco =  apiClient.profileRecco(movie_type, True)

    # log('local recco for ' + movie_type)
    # for title in resRecco['titles']:
    #    log('resRecco:' + title['name'])

    return resRecco


def get_global_recco(movie_type):
    resRecco =  apiClient.profileRecco(movie_type, False)

    # log('global recco for ' + movie_type)
    # for title in resRecco['titles']:
    #    log(title['name'])

    return resRecco


def get_unwatched_episodes():
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

    def onInit(self):
        win = xbmcgui.Window(xbmcgui.getCurrentWindowDialogId())
        win.setProperty("Movie.Title", self.data["name"])
        win.setProperty("Movie.Plot", self.data["plot"])
        win.setProperty("Movie.Cover", self.data["cover_full"])
        # win.setProperty("Movie.Cover", "default.png")

        for i in range(5):
            win.setProperty("Movie.Similar.{0}.Cover".format(i + 1), "default.png")
            
        labels = dict()
        #~ labels['Director'] = self.data['']
        #~ labels['Writer'] = self.data['']
        #~ labels['Runtime'] = self.data['']
        labels['Release date'] = datetime.fromtimestamp(self.data['date']).strftime('%x')

        xlabels = dict()
        if self.data.has_key('xbmc_movie_detail'):
            xlabels["Director"] = self.data['xbmc_movie_detail']['director']
            xlabels["Writer"] = self.data['xbmc_movie_detail']['writer']
            xlabels["Runtime"] = self.data['xbmc_movie_detail']['runtime'] + ' min'
            xlabels["Release date"] = self.data['xbmc_movie_detail']['premiered']
            tFile = self.data['xbmc_movie_detail'].get('file')
            xbmc.log('file:' + str(tFile))
            if tFile:
                win.setProperty("Movie.File", tFile)
                self.getControl(5).setEnabled(True)

        labels.update(xlabels)

        # set available labels
        i = 1
        for key in labels.keys():
            win.setProperty("Movie.Label.{0}.1".format(i), key)
            win.setProperty("Movie.Label.{0}.2".format(i), labels[key])
            i = i + 1


        # similars
        i = 1
        if self.data.has_key('similars'):
            for item in self.data['similars']:
                win.setProperty("Movie.Similar.{0}.Label".format(i), item['name'])
                win.setProperty("Movie.Similar.{0}.Cover".format(i), item['cover_medium'])
                i = i + 1

        tmpTrail = self.data.get('trailer')
        if tmpTrail:
            _youid = tmpTrail.split("/")
            _youid.reverse()
            win.setProperty("Movie.Trailer.Id", str(_youid[0]))
        else:
            self.getControl(10).setEnabled(False)


    def onClick(self, controlId):
        log('onClick: ' + str(controlId))
        if controlId == 5: # play
            self.close()
        if controlId == 6: # add to list
            dialog = xbmcgui.Dialog()
            ret = dialog.select('Choose list', ['Watch later', 'Action', 'Favorite'])
        if controlId == 10: # trailer
            self.close()
        if controlId == 11: # already watched
            rating = get_rating()
            if rating < 4:
                set_already_watched(self.data['id'], rating)

    def onFocus(self, controlId):
        self.controlId = controlId

    def onAction(self, action):
        if (action.getId() in CANCEL_DIALOG):
            self.close()


def add_directory(name, url, mode, iconimage, atype, view_mode=500):
    u = sys.argv[0]+"?url="+uniquote(url)+"&mode="+str(mode)+"&name="+uniquote(name)+"&type="+str(atype)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    # liz.setInfo(type="Video", infoLabels={"Title": name} )
    liz.setProperty("Fanart_Image", addonPath + 'fanart.jpg')
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
    xbmc.executebuiltin("Container.SetViewMode({0})".format(view_mode))
    return ok


def add_movie(movie, url, mode, iconimage, movieid, view_mode=500):
    json_data = json.dumps(movie)
    u = sys.argv[0]+"?url="+uniquote(url)+"&mode="+str(mode)+"&name="+uniquote(movie.get('name'))+"&data="+uniquote(json_data)
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
    add_directory("Movie Recommendations", "url", 1, "list.png", 1)
    add_directory("TV Show", "url", 11, "list.png", 1)
    add_directory("Local Movie recommendations", "url", 12, "list.png", 2)
    add_directory("Unwatched TV Show Episodes", "url", 20, "icon.png", 3)
    add_directory("Upcoming TV Episodes", "url", 20, "icon.png", 3)
    add_directory("Login and Settings", "url", 90, "icon.png", 1)

def show_movies(url, type, movie_type, dirhandle):
    errorMsg = None
    try:
        for movie in get_items(type, movie_type):
            log(json.dumps(movie, indent=4))
            movie['type'] = movie_type
            add_movie(movie, "url",
                2, movie.get('cover_medium'), movie.get("id"))
    except AuthenticationError:
        errorMsg = True
    finally:
        xbmcplugin.endOfDirectory(dirhandle)

    if errorMsg:
        if dialog_check_login_correct():
            xbmc.executebuiltin('Container.Refresh')
        else:
            xbmc.executebuiltin('Container.Update(plugin://plugin.video.synopsi, replace)')         
  
    # xbmc.executebuiltin('Container.Update(plugin://plugin.video.synopsi?url=url&mode=999)')



def show_video_dialog(url, name, json_data):
    global stvList, apiClient

    # add xbmc id if available
    if stvList.hasStvId(json_data['id']):
        cacheItem = stvList.getByStvId(json_data['id'])
        json_data['xbmc_id'] = cacheItem['id']
        log('xbmc id:' + str(json_data['xbmc_id']))
        json_data['xbmc_movie_detail'] = get_details('movie', json_data['xbmc_id'], True)

    log('show video:' + json.dumps(json_data, indent=4))

    # get similar movies
    similars = apiClient.titleSimilar(json_data['id'])
    if similars.has_key('titles'):
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

__addon__  = get_current_addon()
addonPath = __addon__.getAddonInfo('path')

__addonname__ = __addon__.getAddonInfo('name')
__cwd__    = __addon__.getAddonInfo('path')
__author__  = __addon__.getAddonInfo('author')
__version__   = __addon__.getAddonInfo('version')

xbmc.log('SYS ARGV:' + str(sys.argv)) 

params = get_params()
xbmc.log(str(params))

url = None
name = None
mode = None
atype = None
data = None

apiClient = AppApiClient.getDefaultClient()
apiClient.login_state_announce = LoginState.AddonDialog
stvList = StvList.getDefaultList(apiClient)

# xbmc.log(str(sys.argv))

try:
    url=uniunquote(params["url"])
except:
    pass
try:
    name=uniunquote(params["name"])
except:
    pass
try:
    mode=int(params["mode"])
except:
    pass
try:
    atype=int(params["type"])
except:
    pass

try:
    data = uniunquote(params["data"])
    json_data = json.loads(data)
except:
    pass
   

dirhandle = int(sys.argv[1])

log('mode: %s type: %s' % (mode, atype))    
log('mode type: %s' % type(mode))   
log('url: %s' % (url))  
log('data: %s' % (data))    

if mode==None or url==None or len(url)<1:
    show_categories()
    xbmcplugin.endOfDirectory(dirhandle)
    xbmcgui.Window(xbmcgui.getCurrentWindowId()).clearProperty("Fanart_Image")
    xbmcgui.Window(xbmcgui.getCurrentWindowId()).setProperty("Fanart_Image", addonPath + 'fanart.jpg')
    xbmcgui.Window(xbmcgui.getCurrentWindowId()).setProperty("Fanart", addonPath + 'fanart.jpg')

    xbmc.executebuiltin("Container.SetViewMode(503)")
elif mode==1:
    show_movies(url, atype, 'movie', dirhandle)
elif mode==11:
    show_movies(url, atype, 'episode', dirhandle)
elif mode==12:
    show_movies(url, atype, 'movie', dirhandle)
elif mode==13:
    show_movies(url, atype, 'episode', dirhandle)
elif mode==20:
    show_movies(url, atype, 'none', dirhandle)
elif mode==2:
    json_data['type'] = atype
    show_video_dialog(url, name, json_data)
elif mode==90:
    __addon__.openSettings()
elif mode==999:
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
    show_video_dialog(0, 0, jdata)
    


