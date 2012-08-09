import xbmc, xbmcgui, xbmcplugin, xbmcaddon
import urllib2, urllib
import re, sys, os, time
import xbmcvfs
import test, json
import os.path

from PIL import Image, ImageDraw, ImageOps
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

        win.setProperty("Movie.Label.1.1", "Text one")
        win.setProperty("Movie.Label.1.2", "Text two")

        # print dir(self)
        # win.setProperty("Movie.Title", "Title")
        # win.setProperty("Movie.Cover", "http://s3.amazonaws.com/titles.synopsi.tv/01982155-267.jpg")
        # lorem = """
        # Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed feugiat, nunc in tempor bibendum, lectus lacus tristique nulla, non porta nulla augue placerat tellus. Nulla consequat pharetra leo, ac imperdiet orci auctor sed. Curabitur placerat mauris tellus, ut commodo justo. Cras dictum dictum luctus. Aenean pharetra faucibus libero in molestie. Donec accumsan bibendum faucibus. Vestibulum ut lectus orci, et rutrum magna. In nec massa mi. Curabitur ut felis sed lectus vulputate aliquam. Pellentesque malesuada porta rhoncus. Praesent sodales augue at tellus laoreet non congue eros varius. Maecenas dui augue, condimentum sed venenatis non, elementum sed orci.

        # Integer sed ipsum ac dolor lacinia scelerisque ut a erat. Proin non tellus quis elit bibendum luctus. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Nunc ut placerat lectus. Nunc imperdiet tellus vel enim fringilla ornare. Integer rhoncus tempor tellus, a eleifend lectus fringilla quis. Quisque vehicula tristique vehicula.

        # Nam lobortis interdum gravida. Pellentesque pellentesque pharetra dolor quis ullamcorper. Maecenas at diam mauris, eu ultrices eros. Ut ac elementum orci. Proin sagittis porta turpis, quis suscipit ligula viverra sit amet. Praesent eu nunc ut ante iaculis tempus pretium id nisl. Vestibulum dictum, magna porttitor tempus rhoncus, enim diam tempus purus, sit amet molestie orci nulla sit amet quam. Aliquam at tellus risus, a vulputate est. Maecenas nunc neque, porttitor et accumsan sit amet, auctor non augue. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Nam pharetra nisi nibh. Sed nec lacus vel tellus volutpat mollis vel quis augue. Suspendisse commodo mi risus. Nunc diam ante, iaculis ac ornare quis, sodales non ante. Integer mattis tempor ante, molestie mollis eros dictum eget.

        # Quisque nulla diam, mattis non scelerisque quis, dignissim ut elit. Proin dolor eros, interdum id dictum vel, feugiat vel odio. Suspendisse convallis, massa nec porttitor tempor, diam augue vestibulum turpis, vel vulputate eros purus et lacus. Mauris volutpat fermentum turpis. Donec ullamcorper felis at elit viverra pulvinar. Cras condimentum est blandit ligula hendrerit a elementum augue tincidunt. In sit amet felis mauris. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; Duis sed lacus est, et interdum lacus. Morbi non erat nibh. Nulla facilisi. Praesent bibendum ante non sapien posuere sit amet facilisis dui fermentum.

        # Quisque ac tortor nisi. Duis urna nisi, varius ac ultricies ut, aliquam eget elit. Phasellus auctor massa a mi faucibus eu viverra turpis accumsan. Suspendisse elementum vehicula sapien, a sodales eros euismod vel. Aenean rutrum tristique tristique. Pellentesque et mauris nisi. Donec pharetra erat mi, volutpat congue augue. Vivamus rhoncus porta semper. Vestibulum ut malesuada dolor. Donec vitae ligula urna.
        # """

        # win.setProperty("Movie.Plot", lorem)
        # self.getControl(5).setEnabled(False)

        # win.setProperty("Movie.Trailer", "http://www.youtube.com/watch?v=-tnxzJ0SSOw")
        # win.setProperty("Movie.Trailer.Id", "LV5_xj_yuhs")
        # win.getControl()
        # win.getControl(49).setProperty("Title", "Title")

        # xbmc.sleep(1000)
        win.setProperty("Movie.Title", "Titsadfsdfasdfl")

        # print self.getProperty("Movie.Title")


        # print self
        # print win

        # print self == win


        # $INFO[ListItem.Writer]
        # win.setProperty("ListItem.Writer", "Title")

        win.setProperty("Movie.Title", self.data["name"])
        win.setProperty("Movie.Cover", self.data["cover_large"])
        win.setProperty("Movie.Plot", self.data["plot"])

        # for i in range(1,13):
        #     win.setProperty("Movie.Label.{0}.1".format(i), "Text one")
        #     win.setProperty("Movie.Label.{0}.2".format(i), "Text two")
        #     win.setProperty("Movie.Label.{0}.3".format(i), "true")

        
        def set_labels(key, value):
            win.setProperty("Movie.Label.{0}.1".format(i), key)
            win.setProperty("Movie.Label.{0}.2".format(i), value)
            i = i + 1

        # set_labels("Director", "Adam Jurko")
        # set_labels("Writer", "John Gatins, Dan Gilroy, Jeremy Leven, Richard Matheson")
        # set_labels("Runtime", "23 min")
        # set_labels("Release date", "September 06, 2011")

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

        if self.data["trailer"]:
            _youid = self.data["trailer"].split("/")
            print _youid
            _youid.reverse()
            print _youid[0]
            win.setProperty("Movie.Trailer.Id", str(_youid[0]))
            # win.setProperty("Movie.Title", self.data["name"])
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
    add_directory("Recommendations", "url", 1, "list.png", 1)
    add_directory("Unwatched TV episodes", "url", 1, "icon.png", 3)
    add_directory("Lists", "url", 1, "icon.png", 4)
    add_directory("Trending Movies", "url", 1, "icon.png", 5, view_mode=500)
    add_directory("Trending TV Shows", "url", 1, "icon.png", 6)


def show_movies(url, type):
    # for film in movies:
    for film in get_items(type):
        add_movie(film.get('name'), "stack://C:\Users\Tommy\Videos\Movies\J Edgar.2011.DVDRip XviD-PADDO\CD1\paddo-jedgar-a.avi , \
         C:\Users\Tommy\Videos\Movies\J Edgar.2011.DVDRip XviD-PADDO\CD2\paddo-jedgar-b.avi",
            2, film.get('cover_medium'), film.get("id"))


def show_video_dialog(url, name, data):
    print data
    ui = VideoDialog("VideoInfo.xml", __cwd__, "Default", data=json.loads(data))
    # ui = VideoDialog("DialogVideoInfo.xml", __cwd__, "Default")
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


if __addon__.getSetting("firststart") == "true":
    xbmc.executebuiltin("RunAddon(service.synopsi)")
    __addon__.setSetting(id='firststart', value="false")

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
