import xbmc, xbmcgui, xbmcplugin, xbmcaddon
import urllib2, urllib
import re, sys, os, time
import xbmcvfs
import test
import os.path


from PIL import Image, ImageDraw, ImageOps
movies = test.jsfile


# CANCEL_DIALOG = (9, 10, 92, 216, 247, 257, 275, 61467, 61448, )
# # ADDON INFORMATION
# __addon__     = xbmcaddon.Addon()
# __addonname__ = __addon__.getAddonInfo('name')
# __cwd__       = __addon__.getAddonInfo('path')
# __author__    = __addon__.getAddonInfo('author')
# __version__   = __addon__.getAddonInfo('version')


# xbmc.Player(xbmc.PLAYER_CORE_AUTO).play(string, item)

# listitem = xbmcgui.ListItem('Ironman')
# listitem.setInfo('video', {'Title': 'Ironman', 'Genre': 'Science Fiction'})

# xbmc.Player( xbmc.PLAYER_CORE_MPLAYER ).play("C:\Users\Tommy\Videos\Movies\A Beautiful Mind 2001 dvdrip.(www.USABIT.com)\A_Butfl_Mnd.part1\A Beautiful Mind 2001 dvdrip.(www.USABIT.com).avi", listitem)

# xbmcplugin.addDirectoryItem()

# while True:
#     if xbmcplugin.addDirectoryItem(int(sys.argv[1]), 'F:\\Trailers\\300.mov', listitem, totalItems=50): break

# for i in range(100):
#     xbmcplugin.addDirectoryItem(int(sys.argv[1]), 'F:\\Trailers\\300.mov', listitem, totalItems=50)


# xbmcplugin.addDirectoryItem(int(sys.argv[1]), 'F:\\Trailers\\300.mov', listitem, totalItems=50)
# xbmcplugin.endOfDirectory(int(sys.argv[1]))


# ui = XMLRatingDialog("Main.xml", __cwd__, "Default", ctime=0,
#                                              tottime=0, token="",
#                                              hashd=[])
# ui.doModal()
# del ui

# xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
# xbmcplugin.endOfDirectory(int(sys.argv[1]))
xbmc.log(str(dir(xbmcvfs)))

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

    im = Image.new("RGBA", (150, 75), "white")
    for i in range(6):
        urllib.urlretrieve (movies[i].get('cover_thumbnail'), tempfile.gettempdir() + "tmp.jpg")
        _im = Image.open(tempfile.gettempdir() + "tmp.jpg")
        y = ImageOps.expand(_im, border=2, fill='white')
        # y.save("tmp.jpg")
        im.paste(y, (0 + 25 * i, 0))
    im.save(tempfile.gettempdir() + "list.png","PNG")


    addDir("Recommendations","url",1,tempfile.gettempdir() + "list.png")
    addDir("Unwatched TV episodes","url",1,"icon.png")
    addDir("Lists","url",1,"icon.png")
    addDir("Trending Movies","url",1,"icon.png", view_mode=500)
    addDir("Trending TV Shows","url",1,"icon.png")


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
        addDir(film.get('name'),"stack://C:\Users\Tommy\Videos\Movies\J Edgar.2011.DVDRip XviD-PADDO\CD1\paddo-jedgar-a.avi , C:\Users\Tommy\Videos\Movies\J Edgar.2011.DVDRip XviD-PADDO\CD2\paddo-jedgar-b.avi",
            2, film.get('cover_medium'))
def VIDEOLINKS(url,name):
    #data = getHTML(url,baseurl)
    
    pl=xbmc.PlayList(1)
    pl.clear()
    """
    episode = re.compile('"url":"(.+?)"').findall(data, re.DOTALL)
    for links in episode:
        if links.split('/')[4] == 'video':
            string = links
    """
    string = url
               
    item=xbmcgui.ListItem(name, iconImage='', thumbnailImage='')       
    item.setInfo( type="Video", infoLabels={ "Title": name})
    xbmc.Player(xbmc.PLAYER_CORE_DVDPLAYER).play(string, item)


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


xbmc.log(xbmc.getSkinDir())

if __addon__.getSetting("firststart") == "true":
    xbmc.executebuiltin("RunAddon(service.synopsi)")
    __addon__.setSetting(id='firststart', value="false")

# WINDOW = xbmcgui.Window()
# # WINDOW.setProperty("Skin.String(Home_Custom_Back_Video_Folder)", __cwd__ + "/resources/skins/Default/media/videos.jpg")
# # special://skin/backgrounds/music.jpg
# WINDOW.setProperty("Skin.String(Home_Custom_Back_Video_Folder)", "special://skin/backgrounds/music.jpg")


xbmc.log(str(__cwd__))

xbmc.log(os.path.join(__cwd__, "resources", "skins"))


xbmc.log(os.path.normpath(os.path.join(__cwd__, "fanart.jpg")))



for i in ["videos.jpg","fanart.jpg", "C://Users//Tommy//AppData//Roaming//XBMC//addons//plugin.video.synopsi//fanart.jpg", os.path.normpath(os.path.join(__cwd__, "fanart.jpg"))]:
    xbmc.log( "{0} {1}".format(i, str(xbmcvfs.exists(i))))



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

print "Mode: "+str(mode)
print "URL: "+str(url)
print "Name: "+str(name)

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
    VIDEOLINKS(url,name)
