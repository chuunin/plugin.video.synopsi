import xbmc, xbmcgui, xbmcplugin, xbmcaddon
import urllib2, urllib
import re, sys, os, time
import xbmcvfs
import test
import os.path

from PIL import Image, ImageDraw, ImageOps
movies = test.jsfile


CANCEL_DIALOG = (9, 10, 92, 216, 247, 257, 275, 61467, 61448, )
# # ADDON INFORMATION
# __addon__     = xbmcaddon.Addon()
# __addonname__ = __addon__.getAddonInfo('name')
# __cwd__       = __addon__.getAddonInfo('path')
# __author__    = __addon__.getAddonInfo('author')
# __version__   = __addon__.getAddonInfo('version')
# xbmcplugin.endOfDirectory(int(sys.argv[1]))
xbmc.log(str(dir(xbmcvfs)))


def get_local_recco():
    return movies


def get_global_recco():
    return movies


def get_unwatched_episodes():
    return movies


def get_lists():
    return movies


def get_trending_movies():
    return movies


def get_trending_tvshows():
    return movies


class XMLRatingDialog(xbmcgui.WindowXMLDialog):
    """
    Dialog class that asks user about rating of movie.
    """
    def __init__(self, *args, **kwargs):
        pass
        self.setProperty("Title", "Title")
        self.setProperty("Movie.Title", "Title")
        self.setProperty("Video.Icon", "https://s3.amazonaws.com/titles.synopsi.tv/01982155-267.jpg")
        self.setProperty("Icon", "C://Users//Tommy//AppData//Roaming//XBMC//addons//plugin.video.synopsi//fanart.jpg")
        # self.getControl(49).setProperty("Title", "Title")

    def message(self, message):
        """
        Shows xbmc dialog with OK and message.
        """
        dialog = xbmcgui.Dialog()
        dialog.ok(" My message title", message)
        self.close()

    def onInit(self):
        pass
        # self.getControl(49).setProperty("Title", "Title")
        # setStaticContent
        lis = []
        liz=xbmcgui.ListItem("Film", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
        liz.setInfo( type="Video", infoLabels={ "Label": "Film" } )

        lis.append(lis)
        self.getControl(49).addItem(liz)
        # self.getControl(49).setStaticContent(items=liz)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

        self.getControl(5).setEnabled(False)


        win = xbmcgui.Window(xbmcgui.getCurrentWindowDialogId())
        win.setProperty("Movie.Title", "Title")
        win.setProperty("Movie.Cover", "http://s3.amazonaws.com/titles.synopsi.tv/01982155-267.jpg")
        lorem = """
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed feugiat, nunc in tempor bibendum, lectus lacus tristique nulla, non porta nulla augue placerat tellus. Nulla consequat pharetra leo, ac imperdiet orci auctor sed. Curabitur placerat mauris tellus, ut commodo justo. Cras dictum dictum luctus. Aenean pharetra faucibus libero in molestie. Donec accumsan bibendum faucibus. Vestibulum ut lectus orci, et rutrum magna. In nec massa mi. Curabitur ut felis sed lectus vulputate aliquam. Pellentesque malesuada porta rhoncus. Praesent sodales augue at tellus laoreet non congue eros varius. Maecenas dui augue, condimentum sed venenatis non, elementum sed orci.

Integer sed ipsum ac dolor lacinia scelerisque ut a erat. Proin non tellus quis elit bibendum luctus. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Nunc ut placerat lectus. Nunc imperdiet tellus vel enim fringilla ornare. Integer rhoncus tempor tellus, a eleifend lectus fringilla quis. Quisque vehicula tristique vehicula.

Nam lobortis interdum gravida. Pellentesque pellentesque pharetra dolor quis ullamcorper. Maecenas at diam mauris, eu ultrices eros. Ut ac elementum orci. Proin sagittis porta turpis, quis suscipit ligula viverra sit amet. Praesent eu nunc ut ante iaculis tempus pretium id nisl. Vestibulum dictum, magna porttitor tempus rhoncus, enim diam tempus purus, sit amet molestie orci nulla sit amet quam. Aliquam at tellus risus, a vulputate est. Maecenas nunc neque, porttitor et accumsan sit amet, auctor non augue. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Nam pharetra nisi nibh. Sed nec lacus vel tellus volutpat mollis vel quis augue. Suspendisse commodo mi risus. Nunc diam ante, iaculis ac ornare quis, sodales non ante. Integer mattis tempor ante, molestie mollis eros dictum eget.

Quisque nulla diam, mattis non scelerisque quis, dignissim ut elit. Proin dolor eros, interdum id dictum vel, feugiat vel odio. Suspendisse convallis, massa nec porttitor tempor, diam augue vestibulum turpis, vel vulputate eros purus et lacus. Mauris volutpat fermentum turpis. Donec ullamcorper felis at elit viverra pulvinar. Cras condimentum est blandit ligula hendrerit a elementum augue tincidunt. In sit amet felis mauris. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; Duis sed lacus est, et interdum lacus. Morbi non erat nibh. Nulla facilisi. Praesent bibendum ante non sapien posuere sit amet facilisis dui fermentum.

Quisque ac tortor nisi. Duis urna nisi, varius ac ultricies ut, aliquam eget elit. Phasellus auctor massa a mi faucibus eu viverra turpis accumsan. Suspendisse elementum vehicula sapien, a sodales eros euismod vel. Aenean rutrum tristique tristique. Pellentesque et mauris nisi. Donec pharetra erat mi, volutpat congue augue. Vivamus rhoncus porta semper. Vestibulum ut malesuada dolor. Donec vitae ligula urna.
        """

        win.setProperty("Movie.Plot", lorem)

        win.setProperty("Movie.Trailer", "http://www.youtube.com/watch?v=-tnxzJ0SSOw")
        win.setProperty("Movie.Trailer.Id", "LV5_xj_yuhs")

        win.setProperty("Movie.Trailer.Id", "LV5_xj_yuhs")

        win.getControl()


        xbmc.sleep(1000)
        win.setProperty("Movie.Title", "Titsadfsdfasdfl")
        # $INFO[ListItem.Writer]
        # win.setProperty("ListItem.Writer", "Title")

    def onClick(self, controlId):
        if controlId == 11:
            pass
        xbmc.log(str(controlId))
        self.close()

    def onFocus(self, controlId):
        self.controlId = controlId

    def onAction(self, action):
        if (action.getId() in CANCEL_DIALOG):
            self.close()


def addDir(name,url,mode,iconimage, view_mode=500):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
    ok=True
    liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": name } )
    liz.setProperty("Fanart_Image", 'C://Users//Tommy//AppData//Roaming//XBMC//addons//plugin.video.synopsi//fanart.jpg')
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
    xbmc.executebuiltin("Container.SetViewMode({0})".format(view_mode))
    return ok

#####
# Need to rewrite completely
#####
def SEASONS():
    #data = json.loads(jsfile.read())
    #addDir('Name','http://video.markiza.sk',1,'link')
    # for film in movies:
    #     #print film.get('cover_medium'), film.get('name')
    #     addDir(film.get('name'),"stack://C:\Users\Tommy\Videos\Movies\J Edgar.2011.DVDRip XviD-PADDO\CD1\paddo-jedgar-a.avi , C:\Users\Tommy\Videos\Movies\J Edgar.2011.DVDRip XviD-PADDO\CD2\paddo-jedgar-b.avi",
    #         2, film.get('cover_medium'))


    
    # im = Image.new("RGBA", (150, 75), "white")
    # for i in range(6):
    #     urllib.urlretrieve (movies[i].get('cover_thumbnail'), "special://temp/tmp.jpg")
    #     _im = Image.open("special://temp/tmp.jpg")
    #     y = ImageOps.expand(_im, border=2, fill='white')
    #     # y.save("special://temp/tmp.jpg")
    #     im.paste(y, (0 + 25 * i, 0))
    # im.save("special://temp/list.png","PNG")


    import tempfile

    # tempfile.gettempdir()

    # im = Image.new("RGBA", (150, 75), "white")
    # for i in range(6):
    #     urllib.urlretrieve (movies[i].get('cover_thumbnail'), tempfile.gettempdir() + "tmp.jpg")
    #     _im = Image.open(tempfile.gettempdir() + "tmp.jpg")
    #     y = ImageOps.expand(_im, border=2, fill='white')
    #     # y.save("tmp.jpg")
    #     im.paste(y, (0 + 25 * i, 0))
    # im.save(tempfile.gettempdir() + "list.png","PNG")

    # im = Image.new("RGBA", (450, 223), "white")
    # for i in range(6):
    #     urllib.urlretrieve (movies[i].get('cover_medium'), tempfile.gettempdir() + "tmp.jpg")
    #     _im = Image.open(tempfile.gettempdir() + "tmp.jpg")
    #     y = ImageOps.expand(_im, border=2, fill='white')
    #     im.paste(y, (0 + 75 * i, 0))
    # im.save(tempfile.gettempdir() + "list.png","PNG")



    addDir("Recommendations","url",1,"list.png")
    addDir("Unwatched TV episodes","url",1,"icon.png")
    addDir("Lists","url",1,"icon.png")
    addDir("Trending Movies","url",1,"icon.png", view_mode=500)
    addDir("Trending TV Shows","url",1,"icon.png")

def add_movie(name,url,mode,iconimage, view_mode=500):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
    ok=True
    liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": "Titulok" } )
    liz.setProperty("Fanart_Image", 'C://Users//Tommy//AppData//Roaming//XBMC//addons//plugin.video.synopsi//fanart.jpg')
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
    xbmc.executebuiltin("Container.SetViewMode({0})".format(view_mode))
    return ok

def show_movie_dialog():
    """
    Show movie dialog.
    """
    ui = XMLRatingDialog("VideoInfo.xml", __cwd__, "Default")
    ui.doModal()
    del ui


def EPISODES(url):
    """
    data = getHTML(url,baseurl)
    
    for image, url, title, date, pv in episodes:
        #addDir(title,bconf + url.split('/')[3],2,image)
        addDir(title +' '+date,bconf + url.split('/')[3],2,image)
    """
    # VIDEOLINKS(url, "Film")

    for film in movies:
        #print film.get('cover_medium'), film.get('name')
        add_movie(film.get('name'),"stack://C:\Users\Tommy\Videos\Movies\J Edgar.2011.DVDRip XviD-PADDO\CD1\paddo-jedgar-a.avi , C:\Users\Tommy\Videos\Movies\J Edgar.2011.DVDRip XviD-PADDO\CD2\paddo-jedgar-b.avi",
            2, film.get('cover_medium'))

def VIDEOLINKS(url,name):
    #data = getHTML(url,baseurl)
    
    # pl=xbmc.PlayList(1)
    # pl.clear()
    """
    episode = re.compile('"url":"(.+?)"').findall(data, re.DOTALL)
    for links in episode:
        if links.split('/')[4] == 'video':
            string = links
    """
    # string = url
               
    # item=xbmcgui.ListItem(name, iconImage='', thumbnailImage='')       
    # item.setInfo( type="Video", infoLabels={ "Title": name})
    # xbmc.Player(xbmc.PLAYER_CORE_DVDPLAYER).play(string, item)


    # ui = XMLRatingDialog("InfoMovieDialog.xml", __cwd__, "Default")
    ui = XMLRatingDialog("VideoInfo.xml", __cwd__, "Default")
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


# def addDir(name,url,mode,iconimage):
#     u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
#     ok=True
#     liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
#     liz.setInfo( type="Video", infoLabels={ "Title": name } )
#     ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
#     return ok
    
          
# $INFO[Skin.String(Home_Custom_Back_Video_Folder)]
# ADDON INFORMATION
__addon__     = xbmcaddon.Addon()
__addonname__ = __addon__.getAddonInfo('name')
__cwd__       = __addon__.getAddonInfo('path')
__author__    = __addon__.getAddonInfo('author')
__version__   = __addon__.getAddonInfo('version')


# xbmc.log(xbmc.getSkinDir())

if __addon__.getSetting("firststart") == "true":
    xbmc.executebuiltin("RunAddon(service.synopsi)")
    __addon__.setSetting(id='firststart', value="false")

# WINDOW = xbmcgui.Window()
# # WINDOW.setProperty("Skin.String(Home_Custom_Back_Video_Folder)", __cwd__ + "/resources/skins/Default/media/videos.jpg")
# # special://skin/backgrounds/music.jpg
# WINDOW.setProperty("Skin.String(Home_Custom_Back_Video_Folder)", "special://skin/backgrounds/music.jpg")


# xbmc.log(str(__cwd__))

# xbmc.log(os.path.join(__cwd__, "resources", "skins"))


# xbmc.log(os.path.normpath(os.path.join(__cwd__, "fanart.jpg")))



# for i in ["videos.jpg","fanart.jpg", "C://Users//Tommy//AppData//Roaming//XBMC//addons//plugin.video.synopsi//fanart.jpg", os.path.normpath(os.path.join(__cwd__, "fanart.jpg"))]:
#     xbmc.log( "{0} {1}".format(i, str(xbmcvfs.exists(i))))



params=get_params()
url=None
name=None
mode=None

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

# print "Mode: "+str(mode)
# print "URL: "+str(url)
# print "Name: "+str(name)

if mode==None or url==None or len(url)<1:
    print ""
    SEASONS()
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    # xbmcgui.Window(xbmcgui.getCurrentWindowId()).setFocusId()
    # xbmc.executebuiltin("Container.SetViewMode(51)")
    # xbmc.executebuiltin("Container.SetViewMode(52)")
    xbmcgui.Window(xbmcgui.getCurrentWindowId()).clearProperty("Fanart_Image")
    xbmcgui.Window(xbmcgui.getCurrentWindowId()).setProperty("Fanart_Image", 'C://Users//Tommy//AppData//Roaming//XBMC//addons//plugin.video.synopsi//fanart.jpg')
    xbmcgui.Window(xbmcgui.getCurrentWindowId()).setProperty("Fanart", 'C://Users//Tommy//AppData//Roaming//XBMC//addons//plugin.video.synopsi//fanart.jpg')

    xbmc.executebuiltin("Container.SetViewMode(503)")
    # standart xbmc.executebuiltin("Container.SetViewMode(50)") 
    # xbmc.executebuiltin("Container.SetViewMode(51)")
elif mode==1:
    print ""+url
    EPISODES(url)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    # xbmc.executebuiltin("Container.SetViewMode(500)")
elif mode==2:
    print ""+url
    VIDEOLINKS(url, name)
    # xbmcplugin.endOfDirectory(int(sys.argv[1]))
