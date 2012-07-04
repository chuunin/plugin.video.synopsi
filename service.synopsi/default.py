import xbmc
import xbmcgui
import xbmcaddon
import json
import urllib2
from urllib2 import HTTPError
import re
import uuid
import os
import sqlite3
import socket
import time
import threading
import sys



#Local imports
import RatingDialog
import lib


class Timer():
   def __enter__(self): self.start = time.time()
   def __exit__(self, *args): xbmc.log(str(time.time() - self.start))

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

def GetHashDic(path):
    """Returns hash dictionary."""
    hashDic = {}
    if not "stack://" in path:
        hashDic['synopsihash'] = str(lib.myhash(path))
        hashDic['subtitlehash'] = str(lib.hashFile(path))
    else:
        hashDic['files'] = []
        for moviefile in path.strip("stack://").split(" , "):
            hashDic['files'].append(
                        {"path":moviefile, 
                        "synopsihash":str(lib.myhash(moviefile)),
                        "subtitlehash":str(lib.hashFile(moviefile))
                        })
    return hashDic

def SendInfoStart(plyer, status):
    """Function that sends json of current video status."""

    InfoTag = plyer.getVideoInfoTag()
    path = plyer.getPlayingFile()

    hashDic = GetHashDic(path)

    data = {'File': InfoTag.getFile(),
            'File2': path, 
            'Hashes':hashDic,
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

def Getmovies(start, end):
    properties =['file', 'imdbnumber',"lastplayed", "playcount"]
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


def searchVideoDB():
    """
    Function that runs on first start and sends whole movie database.
    """
    
    nomovies = Getmovies(0, 1)["result"]["limits"]["total"]

    pack = 20 # how many movies in one JSON

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

        # WriteSectorMovieToCache(movieDict)

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

    # WriteSectorMovieToCache(movieDict)

class Database(object):
    """docstring for Database"""
    def __init__(self):
        path = os.path.dirname(os.path.dirname(__cwd__))

        if os.name == "nt":
            path = path + "\userdata\Database\MyVideos60.db"
        else:
            path = path + "/userdata/Database/MyVideos60.db"


        self.conn = sqlite3.connect(path)
        self.c = self.conn.cursor()

    def runQuery(self, Query):
        return self.c.execute(Query)
        """
        for row in c.execute(Query):
            row
        """
    def close(self):
        self.conn.close()

class XBAPIThread(threading.Thread):
    """docstring for XBAPIThread"""
    def __init__(self):
        super(XBAPIThread, self).__init__()
        self._stop = threading.Event()
        self.sock = socket.socket()
        self.sock.settimeout(None)
        self.sock.connect(("localhost", 9090))

    def run(self):
        """
        while True:
            data = self.sock.recv(1024)
            xbmc.log(str(data))
            if json.loads(str(data)).get("method") == "System.OnQuit":
                sys.exit(4)
        """
        while True:
            data = self.sock.recv(1024)
            xbmc.log(str(data))
            if json.loads(str(data)).get("method") == "System.OnQuit":
                break
        sys.exit(4)
        
    def __del__(self):
        self.sock.close()
    
    def stop(self):
        self.sock.close()
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

def NotifyAll():
    xbmc.executeJSONRPC("""
    {
    "jsonrpc": "2.0", 
    "method": "JSONRPC.NotifyAll", 
    "id": 1, 
    "params": {
        "sender": "xbmc", 
        "message": "message", 
        "data": 1 
        }
    }
    """)


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
#Notification("SynopsiTV","STARTUP")

if __addon__.getSetting("BOOLTOK") == "false":
    Notification("SynopsiTV","Opening Settings")
    __addon__.openSettings()

xbmc.log(__cwd__)
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

            #Storing hash
            path = xbmc.Player().getPlayingFile()
            hashDic = GetHashDic(path)
            self.Hashes = hashDic

    def onPlayBackEnded(self):
        if (VIDEO == 1):
            xbmc.log('SynopsiTV: PLAYBACK ENDED')
            #SendInfoStart(xbmc.Player(),'ended')
            #TODO: dorobit end
            ui = RatingDialog.XMLRatingDialog("SynopsiDialog.xml" , __cwd__, "Default", ctime=curtime, tottime=totaltime, token=__addon__.getSetting("ACCTOKEN"), hashd=self.Hashes)
            ui.doModal()
            del ui
            
    def onPlayBackStopped(self):
        # TODO: fix with json
        xbmc.log("STOPPPPPPPPPPP  " + str(VIDEO)+" Curtime: "+str(curtime))
        
        if (VIDEO == 1):
            xbmc.log('SynopsiTV: PLAYBACK STOPPED')

            #ask about experience when > 70% of film
            #if curtime > totaltime * 0.7:
            if True:    
                ui = RatingDialog.XMLRatingDialog("SynopsiDialog.xml" , __cwd__, "Default", ctime=curtime, tottime=totaltime, token=__addon__.getSetting("ACCTOKEN"), hashd=self.Hashes)
                ui.doModal()
                del ui
            else:
                pass    

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

with Timer():
    searchVideoDB()

thr = XBAPIThread()
thr.start()

NotifyAll()

while (not xbmc.abortRequested):
    if xbmc.Player().isPlayingVideo():
        VIDEO = 1
        curtime = xbmc.Player().getTime()
        totaltime = xbmc.Player().getTotalTime()
    else:
        VIDEO = 0

    #xbmc.sleep(500)
    xbmc.sleep(500)
    xbmc.log("Loooooping")
       
    if (__addon__.getSetting("BOOLTOK") == "false") and (__addon__.getSetting("USER") != "") and (__addon__.getSetting("PASS") != ""):
        if not loginFailed:
            xbmc.log("SynopsiTV: Trying to login")
            Login(__addon__.getSetting("USER"),__addon__.getSetting("PASS"))

if (xbmc.abortRequested):
    if not thr.stopped:
        thr.stop()
    del thr
    xbmc.log('SynopsiTV: Aborting...')
    sys.exit(4)
