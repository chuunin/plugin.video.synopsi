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

import test
import utilities

# from PIL import Image, ImageDraw, ImageOps

movies = test.jsfile


CANCEL_DIALOG = (9, 10, 92, 216, 247, 257, 275, 61467, 61448, )
# xbmc.log(str(dir(xbmcvfs)))


def get_local_recco():
    return movies


def get_global_recco():
    return movies


def get_unwatched_episodes():
    return movies


def get_lists():
    return movies


def get_movies_in_list(listid):
    return movies


def get_trending_movies():
    return movies


def get_trending_tvshows():
    return movies


def get_items(_type):
    if _type == 1:
        return get_global_recco()
    elif _type == 2:
        return get_local_recco()
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

        labels = {
        "Director": "Adam Jurko",
        "Writer": "John Gatins, Dan Gilroy, Jeremy Leven, Richard Matheson",
        "Runtime": "23 min",
        "Release date": "September 06, 2011"
        }

        i = 1
        for key in labels.keys():
            win.setProperty("Movie.Label.{0}.1".format(i), key)
            win.setProperty("Movie.Label.{0}.2".format(i), labels[key])
            i = i + 1

        labels = {
        "Love Actually": "https://s3.amazonaws.com/titles.synopsi.tv/01982155-267.jpg",
        "The Dark Knight Rises": "https://s3.amazonaws.com/titles.synopsi.tv/ae401d45cb2e88bf6337248bbf0249d2-267.jpg",
        "Real Steel": "https://s3.amazonaws.com/titles.synopsi.tv/02444806-267.jpg",
        "Musime si pomahat": "https://s3.amazonaws.com/titles.synopsi.tv/00873171-267.jpg",
        "State of Play": "https://s3.amazonaws.com/titles.synopsi.tv/00021267-267.jpg"
        }

        i = 1
        for key in labels.keys():
            win.setProperty("Movie.Similar.{0}.Label".format(i), key)
            win.setProperty("Movie.Similar.{0}.Cover".format(i), labels[key])
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
        xbmc.log(str(controlId))
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
    liz.setProperty("Fanart_Image", 'C://Users//Tommy//AppData//Roaming//XBMC//addons//plugin.video.synopsi//fanart.jpg')
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
    xbmc.executebuiltin("Container.SetViewMode({0})".format(view_mode))
    return ok


def add_movie(name, url, mode, iconimage, movieid, view_mode=500):
    for mov in get_items(1):# bug
        if mov["id"] == movieid:
            json_data = json.dumps(mov)
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&data="+urllib.quote_plus(json_data)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": "Titulok" } )
    liz.setProperty("Fanart_Image", 'C://Users//Tommy//AppData//Roaming//XBMC//addons//plugin.video.synopsi//fanart.jpg')
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
    xbmc.executebuiltin("Container.SetViewMode({0})".format(view_mode))
    return ok


def show_categories():
    """
    Shows initial categories on home screen.
    """
    print json.dumps(utilities.get_all_movies())
    add_directory("Recommendations", "url", 1, "list.png", 1)
    add_directory("Unwatched TV episodes", "url", 1, "icon.png", 3)
    add_directory("Lists", "url", 1, "icon.png", 4)
    add_directory("Trending Movies", "url", 1, "icon.png", 5, view_mode=500)
    add_directory("Trending TV Shows", "url", 1, "icon.png", 6)


def show_movies(url, type):
    for film in get_items(type):
        add_movie(film.get('name'), "stack://C:\Users\Tommy\Videos\Movies\J Edgar.2011.DVDRip XviD-PADDO\CD1\paddo-jedgar-a.avi , \
         C:\Users\Tommy\Videos\Movies\J Edgar.2011.DVDRip XviD-PADDO\CD2\paddo-jedgar-b.avi",
            2, film.get('cover_medium'), film.get("id"))


def show_video_dialog(url, name, data):
    try:
        win = xbmcgui.Window(xbmcgui.getCurrentWindowDialogId())
    except ValueError, e:
        ui = VideoDialog("VideoInfo.xml", __cwd__, "Default", data=json.loads(data))
        ui.doModal()
        del ui
    else:
        win = xbmcgui.WindowDialog(xbmcgui.getCurrentWindowDialogId())
        win.close()
        ui = VideoDialog("VideoInfo.xml", __cwd__, "Default", data=json.loads(data))
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

# if __addon__.getSetting("firststart") == "true":
#     xbmc.executebuiltin("RunAddon(service.synopsi)")
#     __addon__.setSetting(id='firststart', value="false")

# print sys.argv

params = get_params()
url = None
name = None
mode = None
type = None
data = None


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
except:
    pass

if mode==None or url==None or len(url)<1:
    show_categories()
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    xbmcgui.Window(xbmcgui.getCurrentWindowId()).clearProperty("Fanart_Image")
    xbmcgui.Window(xbmcgui.getCurrentWindowId()).setProperty("Fanart_Image", 'C://Users//Tommy//AppData//Roaming//XBMC//addons//plugin.video.synopsi//fanart.jpg')
    xbmcgui.Window(xbmcgui.getCurrentWindowId()).setProperty("Fanart", 'C://Users//Tommy//AppData//Roaming//XBMC//addons//plugin.video.synopsi//fanart.jpg')

    xbmc.executebuiltin("Container.SetViewMode(503)")
elif mode==1:
    show_movies(url, type)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
elif mode==2:
    show_video_dialog(url, name, data)
