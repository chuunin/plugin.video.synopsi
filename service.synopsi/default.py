"""
This is default file of SynopsiTV service.
"""
import xbmc
import xbmcgui
import xbmcaddon
import json
import re
import uuid
import os
import sqlite3
import socket
import time
import threading
import sys
import types
import hashlib

from urllib2 import HTTPError, URLError

# Local imports
import lib


CANCEL_DIALOG = (9, 10, 92, 216, 247, 257, 275, 61467, 61448, )
# ADDON INFORMATION
__addon__     = xbmcaddon.Addon()
__addonname__ = __addon__.getAddonInfo('name')
__cwd__       = __addon__.getAddonInfo('path')
__author__    = __addon__.getAddonInfo('author')
__version__   = __addon__.getAddonInfo('version')


def generate_deviceid():
    """
    Returns deviceid generated from MAC address.
    """
    uid = str(uuid.getnode())
    sha1 = hashlib.sha1()
    sha1.update(uid)
    return sha1.hexdigest()


def TrySendData(data, token):
    """
    Try to send data.
    """
    try:
        data["timestamp"] = time.time()
        data["deviceid"] = generate_deviceid()
        lib.send_data(data, token)
    except (URLError, HTTPError):
        tmpstring = __addon__.getSetting("SEND_QUEUE")
        try:
            tmpData = json.loads(tmpstring)
        except ValueError:
            tmpData = []

        if type(tmpData) is not types.ListType:
            tmpData = []

        tmpData.append(data)
        tmpstring = json.dumps(tmpData)
        # tmpstring = tmpstring + json.dumps(self.data)

        __addon__.setSetting(id='SEND_QUEUE', value=tmpstring)


class XMLRatingDialog(xbmcgui.WindowXMLDialog):
    """
    Dialog class that asks user about rating of movie.
    """
    def __init__(self, *args, **kwargs):
        self.data = {'event': "Dialog.Rating"}
        self.data['currenttime'] = kwargs['ctime']
        self.data['totaltime'] = kwargs['tottime']
        self.token = kwargs['token']
        self.data['hashes'] = kwargs['hashd']
        #xbmc.log(str(args))

    def message(self, message):
        """
        Shows xbmc dialog with OK and message.
        """
        dialog = xbmcgui.Dialog()
        dialog.ok(" My message title", message)
        self.close()

    def onInit(self):
        pass

    def onClick(self, controlId):
        if controlId == 11:
            xbmc.log("SynopsiTV: Rated Amazing")
            self.data['rating'] = "Amazing"
        elif controlId == 10:
            xbmc.log("SynopsiTV: Rated OK")
            self.data['rating'] = "OK"
        elif controlId == 15:
            xbmc.log("SynopsiTV: Rated Terrible")
            self.data['rating'] = "Terrible"
        else:
            xbmc.log("SynopsiTV: Not Rated")
            self.data['rating'] = "Not Rated"

        #TrySendData(self.data, self.token)
        global queue
        queue.addToQueue(self.data)
        self.close()

    def onFocus(self, controlId):
        self.controlId = controlId

    def onAction(self, action):
        if (action.getId() in CANCEL_DIALOG):
            xbmc.log("SynopsiTV: Not Rated")
            self.data['rating'] = "Not Rated"
            #TrySendData(self.data,self.token)
            global queue
            queue.addToQueue(self.data)
            self.close()


class Timer():
    def __enter__(self):
        self.start = time.time()

    def __exit__(self, *args):
        xbmc.log(str(time.time() - self.start))


def Notification(Name, Text):
    """Sends notification to XBMC."""
    xbmc.executebuiltin('XBMC.Notification(' + str(Name) + ',' +
                        str(Text) + ',1)')


def Login(username, password):
    """Login function."""
    global loginFailed
    try:
        token = lib.get_token(username, password)
        __addon__.setSetting(id='ACCTOKEN', value=token[0])
        __addon__.setSetting(id='REFTOKEN', value=token[1])
        __addon__.setSetting(id='BOOLTOK', value="true")
        #Deleting Password
        pss = '*' * len(password)
        __addon__.setSetting(id='PASS', value=pss)
    except HTTPError, e:
        if e.code == 400:
            if not loginFailed:
                Notification("SynopsiTV", "Login failed")
            loginFailed = True


def get_api_port():
    """
    This function returns TCP port to which is changed XBMC RPC API.
    If nothing is changed return defualt 9090.
    """
    path = os.path.dirname(os.path.dirname(__cwd__))
    if os.name == "nt":
        path = path + "\userdata\advancedsettings.xml"
    else:
        path = path + "/userdata/advancedsettings.xml"

    value = 9090

    if os.path.isfile(path):
        try:
            with open('filename') as _file:
                temp = _file.read()
                if "tcpport" in temp:
                    port = re.compile('<tcpport>(.+?)</tcpport>').findall(temp)
                    if len(port) > 0:
                        value = port[0]
        except (IOError, Exception):
            pass

    return value


def get_hash_array(path):
    """
    Returns hash array of dictionaries.
    """
    hashDic = []
    if not "stack://" in path:
        fileDic = {}
        fileDic['synopsihash'] = str(lib.myhash(path))
        fileDic['subtitlehash'] = str(lib.hashFile(path))
        hashDic.append(fileDic)
    else:
        #hashDic['files'] = []
        for moviefile in path.strip("stack://").split(" , "):
            hashDic.append({"path": moviefile,
                            "synopsihash": str(lib.myhash(moviefile)),
                            "subtitlehash": str(lib.hashFile(moviefile))
                            })
    return hashDic


def SendInfoStart(plyer, status):
    """
    Function that sends json of current video status.
    """

    InfoTag = plyer.getVideoInfoTag()
    path = plyer.getPlayingFile()
    hashDic = get_hash_array(path)

    data = {
        'event': status,
        'moviedetails': {
            "label": InfoTag.getTitle(),
            "imdbnumber": InfoTag.getIMDBNumber(),
            "file": path,
            "currenttime": plyer.getTime(),
            "totaltime": plyer.getTotalTime(),
            "hashes": hashDic
        },
    }
    TrySendData(data, __addon__.getSetting("ACCTOKEN"))


def get_movies(start, end):
    """
    Get movies from xbmc library. Start is the first in list and end is the last.
    """
    properties = ['file', 'imdbnumber', "lastplayed", "playcount"]
    method = 'VideoLibrary.GetMovies'
    dic = {
        'params': {
            'properties': properties,
            'limits': {'end': end, 'start': start}
        },
        'jsonrpc': '2.0',
        'method': method,
        'id': 1
    }

    return json.loads(xbmc.executeJSONRPC(json.dumps(dic)))


def searchVideoDB():
    """
    Function that runs on first start and sends whole movie database.
    """

    nomovies = get_movies(0, 1)["result"]["limits"]["total"]

    pack = 20  # how many movies in one JSON

    for i in range(nomovies // pack):
        start = i * pack
        end = start + pack

        movieDict = get_movies(start, end)

        for j in range(pack):
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
                    movieDict["result"]['movies'][j]['files'].append({
                        "path": moviefile,
                        "synopsihash": str(lib.myhash(moviefile)),
                        "subtitlehash": str(lib.hashFile(moviefile))
                    })
        xbmc.log(str(json.dumps(movieDict)))
        #xbmc.log(str(xbmc.executeJSONRPC(json.dumps(dic))))

    end = nomovies
    start = end - nomovies % pack

    movieDict = get_movies(start, end)
    for j in range(end - start):
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
                movieDict["result"]['movies'][j]['files'].append({
                    "path": moviefile,
                    "synopsihash": str(lib.myhash(moviefile)),
                    "subtitlehash": str(lib.hashFile(moviefile))
                })
    xbmc.log(str(json.dumps(movieDict)))


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


class Searcher(threading.Thread):
    """docstring for Searcher"""
    def __init__(self):
        super(Searcher, self).__init__()

    def run(self):
        global queue

        Notification("SynopsiTV", "Started loading database")

        nomovies = get_movies(0, 1)["result"]["limits"]["total"]
        pack = 20  # how many movies in one JSON

        for i in range(nomovies // pack):
            if not QUITING:
                start = i * pack
                end = start + pack
                movieDict = get_movies(start, end)
                for j in range(pack):
                    path = movieDict["result"]['movies'][j]['file']
                    if not "stack://" in path:
                        hashArr = []
                        hashArr.append({
                            "synopsihash": str(lib.myhash(path)),
                            "subtitlehash": str(lib.hashFile(path))
                        })
                        movieDict["result"]['movies'][j]["hashes"] = hashArr
                    else:
                        movieDict["result"]['movies'][j]['hashes'] = []
                        for moviefile in path.strip("stack://").split(" , "):
                            movieDict["result"]['movies'][j]['hashes'].append({
                                "path": moviefile,
                                "synopsihash": str(lib.myhash(moviefile)),
                                "subtitlehash": str(lib.hashFile(moviefile))
                            })
                xbmc.log(str(json.dumps(movieDict["result"]["movies"])))
                data = {
                    "event": "Library.Add",
                    "movies": movieDict["result"]["movies"]
                }
                queue.addToQueue(data)

        if not QUITING:
            end = nomovies
            start = end - nomovies % pack
            movieDict = get_movies(start, end)
            for j in range(end - start):
                path = movieDict["result"]['movies'][j]['file']
                if not "stack://" in path:
                    hashArr = []
                    # movieDict["result"]['movies'][j]["synopsihash"] = str(lib.myhash(path))
                    # movieDict["result"]['movies'][j]["subtitlehash"] = str(lib.hashFile(path))
                    hashArr.append({
                        "synopsihash": str(lib.myhash(path)),
                        "subtitlehash": str(lib.hashFile(path))})
                    movieDict["result"]['movies'][j]["hashes"] = hashArr
                else:
                    movieDict["result"]['movies'][j]['hashes'] = []
                    for moviefile in path.strip("stack://").split(" , "):
                        movieDict["result"]['movies'][j]['hashes'].append({
                            "path": moviefile,
                            "synopsihash": str(lib.myhash(moviefile)),
                            "subtitlehash": str(lib.hashFile(moviefile))
                        })
            xbmc.log(str(json.dumps(movieDict["result"]["movies"])))
            data = {
                "event": "Library.Add",
                "movies": movieDict["result"]["movies"]
            }
            queue.addToQueue(data)
        Notification("SynopsiTV", "Finished loading database")
        __addon__.setSetting(id='FIRSTRUN', value="false")

    def stop(self):
        """
        Stop thread
        """
        self._stop.set()

    def stopped(self):
        """
        If thread is stopped
        """
        return self._stop.isSet()


class XBAPIThread(threading.Thread):
    """docstring for XBAPIThread"""
    def __init__(self):
        super(XBAPIThread, self).__init__()
        self._stop = threading.Event()
        self.sock = socket.socket()
        self.sock.settimeout(None)
        #self.sock.connect(("localhost", 9090))
        self.sock.connect(("localhost", get_api_port()))

    def run(self):
        def getMovieDetails(movie_id):
            properties = ['file', 'imdbnumber', "lastplayed", "playcount"]
            method = 'VideoLibrary.GetMovieDetails'
            dic = {'params': {
                'properties': properties,
                'movieid': movie_id  # s 1 e 2 writes 2
            },
                'jsonrpc': '2.0',
                'method': method,
                'id': 1
            }
            return json.loads(xbmc.executeJSONRPC(json.dumps(dic)))
        while True:
            data = self.sock.recv(1024)
            xbmc.log(str(data))
            try:
                data_json = json.loads(str(data))
                method = data_json.get("method")
            except ValueError, e:
                QUITING = True
                break
                method = ""
            # data_json = json.loads(str(data))
            # method = data_json.get("method")
            

            if method == "VideoLibrary.OnRemove":
                # {"jsonrpc":"2.0","method":"VideoLibrary.OnRemove",
                # "params":{"data":{"id":3,"type":"movie"},"sender":"xbmc"}}
                TrySendData({
                    "event": "Library.Remove",
                    "id": data_json["params"]["data"]["id"]
                }, __addon__.getSetting("ACCTOKEN"))
            elif method == "VideoLibrary.OnUpdate":
                details = getMovieDetails(data_json["params"]["data"]["item"]["id"])
                # TrySendData({"Event": "Library.AddORupdate",
                # "ID": data_json["params"]["data"]["item"]["id"],
                # "Details" : details},__addon__.getSetting("ACCTOKEN"))
                TrySendData({
                    "event": "Library.AddORupdate",
                    "id": data_json["params"]["data"]["item"]["id"],
                    "moviedetails": details["result"]["moviedetails"]
                }, __addon__.getSetting("ACCTOKEN"))

            if method == "System.OnQuit":
                # Check if not search running
                QUITING = True
                break

            if method == "Player.OnStop" and (data_json["params"]["data"] is not None):
                if data_json["params"]["data"]["item"]["type"] == "movie" and VIDEO == 0:
                    details = getMovieDetails(data_json["params"]["data"]["item"]["id"])
                    xbmc.log(str(details))
                    ui = XMLRatingDialog("SynopsiDialog.xml", __cwd__, "Default", ctime="",
                                         tottime="", token=__addon__.getSetting("ACCTOKEN"),
                                         hashd=get_hash_array(details["result"]["moviedetails"]["file"]))
                    ui.doModal()
                    del ui

        sys.exit(4)

    def __del__(self):
        self.sock.close()

    def stop(self):
        self.sock.close()
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()


class QueueWorker(threading.Thread):
    """Thread that waits for signals that needs to be send or processed."""
    def __init__(self):
        super(QueueWorker, self).__init__()
        self.queue = []

    def run(self):
        while (not QUITING) and (not xbmc.abortRequested):
            if len(self.queue) == 0:
                xbmc.sleep(1000)
            else:
                for data in self.queue:
                    TrySendData(data, __addon__.getSetting("ACCTOKEN"))
                self.queue = []

    def addToQueue(self, data):
        self.queue.append(data)


def NotifyAll():
    """
    Notifiy all listeners of API in order to test our listener.
    """
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


def check_send_queue():
    """
    Function that checks offline queue.
    """
    tmpstring = __addon__.getSetting("SEND_QUEUE")
    try:
        tmpData = json.loads(tmpstring)
    except ValueError:
        tmpData = []

    if type(tmpData) is not types.ListType:
        tmpData = []
    xbmc.log("BEFORE SEND")
    if tmpData:
        try:
            #xbmc.log(str(json.dumps(tmpData)))
            xbmc.log(str(tmpData))
            lib.send_data({"array": tmpData}, __addon__.getSetting("ACCTOKEN"))
            __addon__.setSetting(id='SEND_QUEUE', value="[]")
        except (URLError, HTTPError):
            pass

class SynopsiPlayer(xbmc.Player):
    """
    Inherited main player class with events.
    """
    xbmc.log('SynopsiTV: Class player is opened')

    def __init__(self):
        xbmc.Player.__init__(self)
        xbmc.log('SynopsiTV: Class player is initialized')
        self.hashes = {}

    def onPlayBackStarted(self):
        #global PLAYING
        if xbmc.Player().isPlayingVideo():
            #PLAYING = True
            xbmc.log('SynopsiTV: PLAYBACK STARTED')
            SendInfoStart(xbmc.Player(), 'Player.Started')

            #Storing hash
            path = xbmc.Player().getPlayingFile()
            hashDic = get_hash_array(path)
            self.hashes = hashDic

    def onPlayBackEnded(self):
        pass
        # if (VIDEO == 1):
        #     xbmc.log('SynopsiTV: PLAYBACK ENDED')
        #     #SendInfoStart(xbmc.Player(),'ended')
        #     TODO: dorobit end
        #     ui = XMLRatingDialog("SynopsiDialog.xml" , __cwd__, "Default", ctime=curtime, 
        #     tottime=totaltime, token=__addon__.getSetting("ACCTOKEN"), hashd=self.Hashes)
        #     ui.doModal()
        #     del ui
        #     #PLAYING = False

    def onPlayBackStopped(self):
        # TODO: fix with json
        xbmc.log("STOPPPPPPPPPPP  " + str(VIDEO) + " Curtime: " + str(curtime))
        # if (VIDEO == 1):
        #     xbmc.log('SynopsiTV: PLAYBACK STOPPED')

        #     #ask about experience when > 70% of film
        #     #if curtime > totaltime * 0.7:
        #     if True:    
        #         ui = XMLRatingDialog("SynopsiDialog.xml" , __cwd__, "Default", ctime=curtime, 
        #         tottime=totaltime, token=__addon__.getSetting("ACCTOKEN"), hashd=self.Hashes)
        #         ui.doModal()
        #         del ui
        #     else:
        #         pass    
        #     #PLAYING = False

    def onPlayBackPaused(self):
        if xbmc.Player().isPlayingVideo():
            xbmc.log('SynopsiTV: PLAYBACK PAUSED')
            SendInfoStart(xbmc.Player(), 'Player.Paused')

    def onPlayBackResumed(self):
        if xbmc.Player().isPlayingVideo():
            xbmc.log('SynopsiTV: PLAYBACK RESUMED')
            SendInfoStart(xbmc.Player(), 'Player.Resumed')

PLAYER = SynopsiPlayer()
QUITING = False

def main():
    xbmc.log('SynopsiTV: Addon information')
    xbmc.log('SynopsiTV: ----> Addon name    : ' + __addonname__)
    xbmc.log('SynopsiTV: ----> Addon path    : ' + __cwd__)
    xbmc.log('SynopsiTV: ----> Addon author  : ' + __author__)
    xbmc.log('SynopsiTV: ----> Addon version : ' + __version__)

    xbmc.log('SynopsiTV: STARTUP')
    Notification("SynopsiTV","STARTUP")

    if __addon__.getSetting("BOOLTOK") == "false":
        Notification("SynopsiTV", "Opening Settings")
        __addon__.openSettings()

    xbmc.log(__cwd__)
    xbmc.log('SynopsiTV: NEW CLASS PLAYER')

    
    loginFailed = False
    curtime, totaltime = (0, 0)

    """
    with Timer():
        searchVideoDB()
    """
    

    check_send_queue()

    if __addon__.getSetting("FIRSTRUN") == "true":
        serThr = Searcher()
        serThr.start()

    thr = XBAPIThread()
    thr.start()

    queue = QueueWorker()
    queue.start()

    NotifyAll()

    # xbmc.executebuiltin('Skin.SetString(SynopsiTV,31323)')
    while (not xbmc.abortRequested):

        # TODO: rewrite to TCP client - its faster
        if xbmc.Player().isPlayingVideo():
            VIDEO = 1
            curtime = xbmc.Player().getTime()
            totaltime = xbmc.Player().getTotalTime()
        else:
            VIDEO = 0

        xbmc.sleep(1000)

        if (
            (__addon__.getSetting("BOOLTOK") == "false") and 
            (__addon__.getSetting("USER") != "") and 
            (__addon__.getSetting("PASS") != "")
            ):
            if not loginFailed:
                xbmc.log("SynopsiTV: Trying to login")
                Login(__addon__.getSetting("USER"), __addon__.getSetting("PASS"))

    if (xbmc.abortRequested):
        if not thr.stopped:
            thr.stop()
        del thr

        # if not serThr.stopped:
        #     serThr.stop()
        # del serThr

        xbmc.log('SynopsiTV: Aborting...')
        sys.exit(4)

if __name__ == "__main__":
    main()