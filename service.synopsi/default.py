import xbmc
import xbmcgui
import xbmcaddon
import json
import urllib2
from urllib2 import HTTPError
import re
import uuid
#Local imports
import RatingDialog
import lib

import hashlib


def Notification(Name, Text):
    """Sends notification to XBMC."""
    xbmc.executebuiltin('XBMC.Notification(' + str(Name) +',' + str(Text) +',1)')

def Login(username, password):
    """Login function."""
    global loginFailed
    try:
        pass
        token = lib.get_token(username, password)
        __addon__.setSetting(id='ACCTOKEN', value=token[0])
        __addon__.setSetting(id='REFTOKEN', value=token[1])
        __addon__.setSetting(id='BOOLTOK', value="true")
        #Deleting Password
        pss  = '*'*len(password)
        __addon__.setSetting(id='PASS', value=pss)
    except HTTPError, e:
        if e.code == 400:
            if not loginFailed:
                Notification("SynopsiTV","Login failed")
            loginFailed = True

def GenerateOSInfo():
    """Function that generates unique device info."""
    uid = str(uuid.uuid4())
    #TODO: Add OS specific info.


def SendInfoStart(plyer, status):
    """Function that sends json of current video status."""
    InfoTag = plyer.getVideoInfoTag()
    data = {'File': InfoTag.getFile(),
            'File2': plyer.getPlayingFile(),
            'Time': plyer.getTime(),
            'TotalTime': plyer.getTotalTime(),
            #'SeekTime': plyer.seekTime(),
            'Path': InfoTag.getPath(),
            'Title': InfoTag.getTitle(),
            'IMDB': InfoTag.getIMDBNumber(),
            'Status': status}
    #xbmc.log(json.dumps(data))
    lib.send_data(data,__addon__.getSetting("ACCTOKEN"))

    """
    req=urllib2.Request('http://dev.synopsi.tv/api/desktop/', data=json.dumps({'data':data, 'token': 12345}),
                        headers={'content-type':'application/json', 'user-agent': 'linux'},
                        origin_req_host='dev.synopsi.tv')
    f = urllib2.urlopen(req)
    
    xbmc.log('SynopsiTV: Response: ' + f.read())
    """

def runQuery():
    #xbmc.log(str(xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": {"properties": ["file", "fanart", "thumbnail"]}, "id": 1}')))
    xbmc.log(str(xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": {"properties": ["file","imdbnumber"]}, "id": 1}')))
    #xbmc.log(str(xbmc.getInfoLabel()))

    properties =['file', 'imdbnumber']
    method = 'VideoLibrary.GetMovies'
#limits=
    dic = {'params': 
    {
    'properties': properties, 
    'limits': {'end': 5, 'start': 0 }
    },
    'jsonrpc': '2.0',
    'method': method,
    'id': 1}

    xbmc.log(str(xbmc.executeJSONRPC(json.dumps(dic))))


    xbmc.log(str(xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "JSONRPC.Permission", "id": 1}')))

def searchVideoDB():
    def Getmovies(start, end):
        properties =['file', 'imdbnumber']
        method = 'VideoLibrary.GetMovies'
        dic = {'params': 
        {
        'properties': properties, 
        'limits': {'end': end, 'start': start } #s 1 e 2 writes 2
        },
        'jsonrpc': '2.0',
        'method': method,
        'id': 1}

        return json.loads(xbmc.executeJSONRPC(json.dumps(dic)))

    nomovies = Getmovies(0,1)["result"]["limits"]["total"]

    pack = 20 #how many movies in one JSON

    for i in range(nomovies//pack):
        start = i*pack
        end = start + pack

        movieDict = Getmovies(start, end)

        for j in range(pack):
            #xbmc.log(str(movieDict["result"]['movies'][j]['label']))
            #xbmc.log(str(lib.myhash(movieDict["result"]['movies'][j]['file'])))

            path = movieDict["result"]['movies'][j]['file']
            if not "stack://" in path:
                #xbmc.log(str(lib.myhash(path)))
                #xbmc.log(str(lib.hashFile(path)))
                movieDict["result"]['movies'][j]["synopsihash"] = str(lib.myhash(path))
                movieDict["result"]['movies'][j]["subtitlehash"] = str(lib.hashFile(path))
            else:
                movieDict["result"]['movies'][j]['files'] = []
                for moviefile in path.strip("stack://").split(" , "):
                    #xbmc.log(str(lib.myhash(moviefile)))
                    movieDict["result"]['movies'][j]['files'].append(
                        {"path":moviefile, 
                        "synopsihash":str(lib.myhash(moviefile)),
                        "subtitlehash":str(lib.hashFile(moviefile))
                        })
        xbmc.log(str(json.dumps(movieDict)))

        #xbmc.log(str(xbmc.executeJSONRPC(json.dumps(dic))))
    
    end = nomovies
    start = end- nomovies%pack

    movieDict = Getmovies(start, end)
    for j in range(end-start):
        #xbmc.log(str(movieDict["result"]["movies"][j]['label']))
        path = movieDict["result"]['movies'][j]['file']
        if not "stack://" in path:
            #xbmc.log(str(lib.myhash(path)))
            #xbmc.log(str(lib.hashFile(path)))
            movieDict["result"]['movies'][j]["synopsihash"] = str(lib.myhash(path))
            movieDict["result"]['movies'][j]["subtitlehash"] = str(lib.hashFile(path))
        else:
            movieDict["result"]['movies'][j]['files'] = []
            for moviefile in path.strip("stack://").split(" , "):
                #xbmc.log(str(lib.myhash(moviefile)))
                movieDict["result"]['movies'][j]['files'].append(
                    {"path":moviefile, 
                    "synopsihash":str(lib.myhash(moviefile)),
                    "subtitlehash":str(lib.hashFile(moviefile))
                    })
    xbmc.log(str(json.dumps(movieDict)))




# ADDON INFORMATION
__addon__     = xbmcaddon.Addon()
__addonname__ = __addon__.getAddonInfo('name')
__cwd__       = __addon__.getAddonInfo('path')
__author__    = __addon__.getAddonInfo('author')
__version__   = __addon__.getAddonInfo('version')
xbmc.log('SynopsiTV: Addon information')
xbmc.log('SynopsiTV: ----> Addon name    : ' + __addonname__)
xbmc.log('SynopsiTV: ----> Addon path    : ' + __cwd__)
xbmc.log('SynopsiTV: ----> Addon author  : ' + __author__ )
xbmc.log('SynopsiTV: ----> Addon version : ' + __version__)

xbmc.log('SynopsiTV: STARTUP')
#Notification("SynopsiTV: STARTUP")


if __addon__.getSetting("BOOLTOK") == "false":
    Notification("SynopsiTV","Opening Settings")
    __addon__.openSettings()


xbmc.log('SynopsiTV: NEW CLASS PLAYER')
class SynopsiPlayer(xbmc.Player) :
    xbmc.log('SynopsiTV: Class player is opened')
    
    def __init__ (self):
        xbmc.Player.__init__(self)
        xbmc.log('SynopsiTV: Class player is initialized')
        
    def onPlayBackStarted(self):
        if xbmc.Player().isPlayingVideo():
            xbmc.log('SynopsiTV: PLAYBACK STARTED')
            SendInfoStart(xbmc.Player(),'started')
            
    def onPlayBackEnded(self):
        if (VIDEO == 1):
            xbmc.log('SynopsiTV: PLAYBACK ENDED')
            #SendInfoStart(xbmc.Player(),'ended')
            #TODO: dorobit end
            ui = RatingDialog.XMLRatingDialog("SynopsiDialog.xml" , __cwd__, "Default", ctime=curtime, tottime=totaltime, token=__addon__.getSetting("ACCTOKEN"))
            ui.doModal()
            del ui
            
    def onPlayBackStopped(self):
        if (VIDEO == 1):
            xbmc.log('SynopsiTV: PLAYBACK STOPPED')

            #ask about experience when > 70% of film

            if curtime > totaltime * 0.7:
                ui = RatingDialog.XMLRatingDialog("SynopsiDialog.xml" , __cwd__, "Default", ctime=curtime, tottime=totaltime, token=__addon__.getSetting("ACCTOKEN"))
                ui.doModal()
                del ui
            else:
                pass                    

            ######
            #ui = RatingDialog.XMLRatingDialog("SynopsiDialog.xml" , __cwd__, "Default", ctime=curtime, tottime=totaltime)
            #ui.doModal()
            #del ui
            #SendInfoStart(xbmc.Player(),'stopped')
            #TODO: dorobit stop
            
    def onPlayBackPaused(self):
        if xbmc.Player().isPlayingVideo():
            xbmc.log('SynopsiTV: PLAYBACK PAUSED')
            SendInfoStart(xbmc.Player(),'paused')
            
    def onPlayBackResumed(self):
        if xbmc.Player().isPlayingVideo():
            xbmc.log('SynopsiTV: PLAYBACK RESUMED')
            SendInfoStart(xbmc.Player(),'resumed')
            

player=SynopsiPlayer()
loginFailed = False
curtime, totaltime = (0,0)
#runQuery()
searchVideoDB()

while (not xbmc.abortRequested):
    if xbmc.Player().isPlayingVideo():
        VIDEO = 1
        curtime = xbmc.Player().getTime()
        totaltime = xbmc.Player().getTotalTime()
    else:
        VIDEO = 0

    xbmc.sleep(500)
    if (__addon__.getSetting("BOOLTOK") == "false") and (__addon__.getSetting("USER") != "") and (__addon__.getSetting("PASS") != ""):
        if not loginFailed:
            xbmc.log("SynopsiTV: Trying to login")
            Login(__addon__.getSetting("USER"),__addon__.getSetting("PASS"))

while (xbmc.abortRequested):
    xbmc.log('SynopsiTV: Aborting...')

