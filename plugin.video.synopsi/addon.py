import xbmc, xbmcgui, xbmcplugin, xbmcaddon
import urllib2, urllib
import re, sys, os, time
import test

movies = test.jsfile


def SEASONS():
    #data = json.loads(jsfile.read())
    #addDir('Name','http://video.markiza.sk',1,'link')
    for film in movies:
        #print film.get('cover_medium'), film.get('name')
        addDir(film.get('name'),film.get('cover_medium'),1,film.get('cover_medium'))

def EPISODES(url):
    data = getHTML(url,baseurl)
    episodes = re.compile(""" <div class="image"><a href=".+?"><img src="(.+?)" /></a></div>
 <div class="title"><a href="(.+?)">(.+?)</a></div>
 <span>(.+?)<br/>(.+?)</span>""").findall(data, re.DOTALL)
    for image, url, title, date, pv in episodes:
        #addDir(title,bconf + url.split('/')[3],2,image)
        addDir(title +' '+date,bconf + url.split('/')[3],2,image)

def VIDEOLINKS(url,name):
    data = getHTML(url,baseurl)
    pl=xbmc.PlayList(1)
    pl.clear()
    episode = re.compile('"url":"(.+?)"').findall(data, re.DOTALL)
    for links in episode:
        if links.split('/')[4] == 'video':
            string = links
               
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


def addDir(name,url,mode,iconimage):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
    ok=True
    liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": name } )
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
    return ok
    
          
# ADDON INFORMATION
__addon__     = xbmcaddon.Addon()
__addonname__ = __addon__.getAddonInfo('name')
__cwd__       = __addon__.getAddonInfo('path')
__author__    = __addon__.getAddonInfo('author')
__version__   = __addon__.getAddonInfo('version')

if __addon__.getSetting("firststart") == "true":
    xbmc.executebuiltin("RunAddon(service.synopsi)")
    __addon__.setSetting(id='firststart', value="false")


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
    xbmc.executebuiltin("Container.SetViewMode(500)")
elif mode==1:
    print ""+url
    EPISODES(url)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
elif mode==2:
    print ""+url
    VIDEOLINKS(url,name)
