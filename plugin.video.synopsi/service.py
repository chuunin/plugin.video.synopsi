"""
This is default file of SynopsiTV service.
"""
import hashlib
import json
import os
import re
import socket
import sqlite3
import sys
import threading
import time
import types
import uuid
import xbmc
import xbmcaddon
import xbmcgui

from urllib2 import HTTPError, URLError

# Local imports
import lib


CANCEL_DIALOG = (9, 10, 92, 216, 247, 257, 275, 61467, 61448, )

__addon__     = xbmcaddon.Addon()
__addonname__ = __addon__.getAddonInfo('name')
__cwd__       = __addon__.getAddonInfo('path')
__author__    = __addon__.getAddonInfo('author')
__version__   = __addon__.getAddonInfo('version')
__language__   = __addon__.getLocalizedString


def get_library_cache():
    """
    Get library cache object.
    """
    return json.loads(__addon__.getSetting("LIBRARY"))


def save_library_cache():
    """
    Save library from memory to file.
    """
    global LIBRARY_CACHE
    __addon__.setSetting(id="LIBRARY", value=LIBRARY_CACHE)


def add_to_library_cache(lib_id, stv_id, hash, lib_type):
    global LIBRARY_CACHE
    LIBRARY_CACHE[hash] = {
        "id" : lib_id,
        "stvid" : stv_id,
        "type" : lib_type
    }


def lc_get_hash_by_id(_id, _type):
    global LIBRARY_CACHE
    return [k for k, v in LIBRARY_CACHE.iteritems() if v["id"] == _id and v["type"] == _type]


def lc_get_id_by_hash(_hash):
    global LIBRARY_CACHE
    return (LIBRARY_CACHE[_hash]["id"], LIBRARY_CACHE[_hash]["type"])


def lc_get_hash_by_stvid(stvid):
    global LIBRARY_CACHE
    return [k for k, v in LIBRARY_CACHE.iteritems() if v["stvid"] == stvid]


def lc_get_stvid_by_hash(_hash):
    global LIBRARY_CACHE
    return LIBRARY_CACHE[_hash]["stvid"]


def lc_get_id_by_stvid(stvid):
    global LIBRARY_CACHE
    return [(v["id"], v["type"]) for v in LIBRARY_CACHE.values() if v["stvid"] == stvid]


def lc_get_stvid_by_id(_id, _type):
    global LIBRARY_CACHE
    return [v["stvid"] for v in LIBRARY_CACHE.values() if v["id"] == _id and v["type"] == _type]


def notification(name, text):
    """
    Sends notification to XBMC.
    """
    xbmc.executebuiltin("XBMC.Notification({0},{1},1)".format(name, text))


def notify_dev(name, text):
    """
    Sends notification only if development mode is active.
    """
    if __addon__.getSetting("DEBUG") == "true":
        xbmc.executebuiltin("XBMC.Notification({0},{1},1)".format(name, text))


def get_token():
    """
    Returns access token.
    """
    return __addon__.getSetting("ACCTOKEN")


def notify_all():
    """
    Notifiy all listeners of API in order to test our listener.
    """
    xbmc.executeJSONRPC(
    """
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
    """
    )


def get_protected_folders():
    """
    Returns array of protected folders.
    """
    array = []
    if __addon__.getSetting("PROTFOL") == "true":
        num_folders = int(__addon__.getSetting("NUMFOLD")) + 1
        for i in range(num_folders):
            path = __addon__.getSetting("FOLDER{0}".format(i + 1))
            array.append(path)

    return array


def is_protected(path):
    """
    If file is protected.
    """
    protected = get_protected_folders()
    for _file in protected:
        if _file in path:
            notification("Ignoring file", str(path))
            return True

    return False


def generate_deviceid():
    """
    Returns deviceid generated from MAC address.
    """
    uid = str(uuid.getnode())
    sha1 = hashlib.sha1()
    sha1.update(uid)
    return sha1.hexdigest()


def get_hash_array(path):
    """
    Returns hash array of dictionaries.
    """
    hash_array = []
    if not "stack://" in path:
        file_dic = {}

        stv_hash = lib.myhash(path)
        sub_hash = lib.hashFile(path)

        if stv_hash:
            file_dic['synopsihash'] = stv_hash
        if sub_hash:
            file_dic['subtitlehash'] = sub_hash

        if  sub_hash or stv_hash:
            hash_array.append(file_dic)

    else:
        for moviefile in path.strip("stack://").split(" , "):
            hash_array.append({"path": moviefile,
                            "synopsihash": str(lib.myhash(moviefile)),
                            "subtitlehash": str(lib.hashFile(moviefile))
                            })
    return hash_array


def get_api_port():
    """
    This function returns TCP port to which is changed XBMC RPC API.
    If nothing is changed return default 9090.
    """
    path = os.path.dirname(os.path.dirname(__cwd__))
    if os.name == "nt":
        path = path + "\userdata\advancedsettings.xml"
    else:
        path = path + "/userdata/advancedsettings.xml"

    value = 9090

    if os.path.isfile(path):
        try:
            with open(path, 'r') as _file:
                temp = _file.read()
                if "tcpport" in temp:
                    port = re.compile('<tcpport>(.+?)</tcpport>').findall(temp)
                    if len(port) > 0:
                        value = port[0]
        except (IOError, IndexError):
            pass

    return value


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


def get_tvshows(start, end):
    """
    Get movies from xbmc library. Start is the first in list and end is the last.
    """
    properties = ['file', 'imdbnumber', "lastplayed", "playcount", "episode"]
    method = 'VideoLibrary.GetTVShows'
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


def get_episodes(twshow_id, season=-1):
    """
    Get episodes from xbmc library.
    """
    properties = ['file', "lastplayed", "playcount", "season", "episode"]
    method = 'VideoLibrary.GetEpisodes'
    if season == -1:
        prms = {
            'properties': properties,
            'tvshowid': twshow_id
        }
    else:
        prms = {
            'properties': properties,
            'tvshowid': twshow_id,
            'season': season
        }
    dic = {
        'params': prms,
        'jsonrpc': '2.0',
        'method': method,
        'id': 1
    }

    return json.loads(xbmc.executeJSONRPC(json.dumps(dic)))


def get_movie_details(movie_id, all_prop=False):
    """
    Get dict of movie_id details.
    """
    if all_prop:
        properties = [
            "title",
            "genre",
            "year",
            "rating",
            "director",
            "trailer",
            "tagline",
            "plot",
            "plotoutline",
            "originaltitle",
            "lastplayed",
            "playcount",
            "writer",
            "studio",
            "mpaa",
            "cast",
            "country",
            "imdbnumber",
            "premiered",
            "productioncode",
            "runtime",
            # "set",
            "showlink",
            "streamdetails",
            # "top250",
            "votes",
            # "fanart",
            # "thumbnail",
            "file",
            "sorttitle",
            "resume",
            # "setid
        ]
    else:
        properties = ['file', 'imdbnumber', "lastplayed", "playcount"]
    method = 'VideoLibrary.GetMovieDetails'
    dic = {
        'params': {
            'properties': properties,
            'movieid': movie_id  # s 1 e 2 writes 2
        },
        'jsonrpc': '2.0',
        'method': method,
        'id': 1
    }
    return json.loads(xbmc.executeJSONRPC(json.dumps(dic)))


def get_tvshow_details(movie_id):
    """
    Get dict of movie_id details.
    """
    properties = ['file', 'imdbnumber', "lastplayed", "playcount"]
    method = 'VideoLibrary.GetTVShowDetails'
    dic = {
    'params': 
        {
            'properties': properties,
            'movieid': movie_id  # s 1 e 2 writes 2
        },
        'jsonrpc': '2.0',
        'method': method,
        'id': 1
    }

    return json.loads(xbmc.executeJSONRPC(json.dumps(dic)))


def get_episode_details(movie_id):
    """
    Get dict of movie_id details.
    """
    properties = ['file', "lastplayed", "playcount", "season", "episode", "tvshowid"]
    # properties = ["season", "episode"]
    # properties = ['file']
    method = 'VideoLibrary.GetEpisodeDetails'
    dic = {
    'params':
        {
            'properties': properties,
            'episodeid': movie_id
        },
        'jsonrpc': '2.0',
        'method': method,
        'id': 1
    }

    xbmc.log(str(json.dumps(dic)))

    response = xbmc.executeJSONRPC(json.dumps(dic))
    xbmc.log(str(response))
    return json.loads(response)


def try_send_data(data, token):
    """
    Try to send data.
    """
    import collections
    def update(d, u):
        """
        Update dictionary with skipping empty values.
        """

        for k, v in u.iteritems():
            if isinstance(v, collections.Mapping):
                r = update(d.get(k, {}), v)
                d[k] = r
            else:
                if (
                    (u[k] is not None) and not (u[k] == "") and
                    not ("special://" in str(u[k]))
                    ):
                    d[k] = u[k]
        return d
    try:
        data["timestamp"] = time.time()
        data["deviceid"] = generate_deviceid()

        # result = {}
        # result.update((k, v) for k, v in data.iteritems() if ((v is not None) or not (v == "")))
        # update(result, data)

        lib.send_data(data, token)
        xbmc.log(str(json.dumps(data)))
        # lib.send_data(result, token)
        # xbmc.log(str(json.dumps(result)))

    except (URLError, HTTPError):
        tmpstring = __addon__.getSetting("SEND_QUEUE")
        try:
            tmp_data = json.loads(tmpstring)
        except ValueError:
            tmp_data = []

        if type(tmp_data) is not types.ListType:
            tmp_data = []

        tmp_data.append(data)
        tmpstring = json.dumps(tmp_data)
        # tmpstring = tmpstring + json.dumps(self.data)

        __addon__.setSetting(id='SEND_QUEUE', value=tmpstring)


def login(username, password):
    """
    Login function.
    """
    global LOGIN_FAILED
    try:
        token = lib.get_token(username, password)
        __addon__.setSetting(id='ACCTOKEN', value=token[0])
        __addon__.setSetting(id='REFTOKEN', value=token[1])
        __addon__.setSetting(id='BOOLTOK', value="true")
        #Deleting Password
        pss = '*' * len(password)
        __addon__.setSetting(id='PASS', value=pss)
    except HTTPError, err:
        if err.code == 400:
            if not LOGIN_FAILED:
                notification("SynopsiTV", "Login failed")
            LOGIN_FAILED = True


def send_player_status(player, status):
    """
    Function that sends json of current video status.
    """

    info_tag = player.getVideoInfoTag()
    path = player.getPlayingFile()
    hash_array = get_hash_array(path)

    if not IS_PROTECTED:
        data = {
            'event': status,
            'moviedetails': {
                "label": info_tag.getTitle(),
                "imdbnumber": info_tag.getIMDBNumber(),
                "file": path,
                "currenttime": player.getTime(),
                "totaltime": player.getTotalTime(),
                "hashes": hash_array
            },
        }
        queue.add_to_queue(data)


def fill_data_dict(player):
    """
    Fills global dictionary DATA_PACK with file ID.
    """
    global DATA_PACK
    global API_LIBRARY_CACHE

    info_tag = player.getVideoInfoTag()
    path = player.getPlayingFile()
    hash_array = get_hash_array(path)

    if not IS_PROTECTED:
        DATA_PACK = {
            "events": [{
                'event': "Started",
                "timestamp": time.time(),
                "currenttime": player.getTime(),
            }],
            'videodetails': {
                "label": info_tag.getTitle(),
                "imdbnumber": info_tag.getIMDBNumber(),
                "file": path,
                "totaltime": player.getTotalTime(),
                "hashes": hash_array
            },
        }

        if API_LIBRARY_CACHE:
            if API_LIBRARY_CACHE["method"] == "Player.OnPlay":
                DATA_PACK["librarydetails"] = {
                    "id": API_LIBRARY_CACHE["params"]["data"]["item"]["id"],
                    "type": API_LIBRARY_CACHE["params"]["data"]["item"]["type"],
                }


def check_send_queue():
    """
    Function that checks offline queue.
    """
    tmpstring = __addon__.getSetting("SEND_QUEUE")
    try:
        tmp_data = json.loads(tmpstring)
    except ValueError:
        tmp_data = []

    if type(tmp_data) is not types.ListType:
        tmp_data = []
    xbmc.log("BEFORE SEND")
    if tmp_data:
        try:
            #xbmc.log(str(json.dumps(tmp_data)))
            xbmc.log(str(tmp_data))
            lib.send_data({"array": tmp_data}, get_token())
            __addon__.setSetting(id='SEND_QUEUE', value="[]")
        except (URLError, HTTPError):
            pass


class Timer():
    def __enter__(self):
        self.start = time.time()

    def __exit__(self, *args):
        xbmc.log(str(time.time() - self.start))


class Database(object):
    """
    docstring for Database
    """
    def __init__(self):
        path = os.path.dirname(os.path.dirname(__cwd__))

        if os.name == "nt":
            path = path + "\userdata\Database\MyVideos60.db"
        else:
            path = path + "/userdata/Database/MyVideos60.db"

        self.conn = sqlite3.connect(path)
        self.cursor = self.conn.cursor()

    def runQuery(self, Query):
        return self.cursor.execute(Query)
        """
        for row in cursor.execute(Query):
            row
        """
    def close(self):
        self.conn.close()


class Searcher(threading.Thread):
    """
    Searcher Thread for first data export.
    TODO: Add if file hash cannot be computed.
    """
    def __init__(self):
        super(Searcher, self).__init__()

    def run(self):
        global queue
        global QUITING

        movies_count = get_movies(0, 1)["result"]["limits"]["total"]
        tvshows_count = get_tvshows(0,1)["result"]["limits"]["total"]
        
        pack = 20  # chuck, how many movies in one JSON

        if movies_count > 0:
            notification("SynopsiTV", "Started loading database")
            for i in range(movies_count // pack):
                if not QUITING:
                    start = i * pack
                    end = start + pack
                    movie_dict = get_movies(start, end)
                    for j in range(pack):
                        path = movie_dict["result"]['movies'][j]['file']
                        if not is_protected(path): 
                            if not (movie_dict["result"]['movies'][j]['imdbnumber']):
                                movie_dict["result"]["movies"][j] = get_movie_details(
                                    movie_dict["result"]['movies'][j]['movieid'], all_prop=True
                                    )["result"]["moviedetails"]

                            movie_dict["result"]['movies'][j]["hashes"] = get_hash_array(path)
            
                    xbmc.log(str(json.dumps(movie_dict["result"]["movies"])))
                    data = {
                        "event": "Library.Add",
                        "movies": movie_dict["result"]["movies"]
                    }
                    queue.add_to_queue(data)

            if not QUITING:
                end = movies_count
                start = end - movies_count % pack
                movie_dict = get_movies(start, end)
                for j in range(end - start):
                    path = movie_dict["result"]['movies'][j]['file']
                    if not is_protected(path):
                        if not (movie_dict["result"]['movies'][j]['imdbnumber']):
                            movie_dict["result"]["movies"][j] = get_movie_details(
                                movie_dict["result"]['movies'][j]['movieid'], all_prop=True
                            )["result"]["moviedetails"]
                        
                        movie_dict["result"]['movies'][j]["hashes"] = get_hash_array(path)

                xbmc.log(str(json.dumps(movie_dict["result"]["movies"])))
                data = {
                    "event": "Library.Add",
                    "movies": movie_dict["result"]["movies"]
                }
                queue.add_to_queue(data)

            notification("SynopsiTV", "Finished loading database")


        def split_list(alist, wanted_parts=1):
            length = len(alist)
            return [alist[i * length // wanted_parts: (i + 1) * length // wanted_parts]
            for i in range(wanted_parts)]


        if not QUITING:
            tvshows_count = get_tvshows(0, 1)["result"]["limits"]["total"]
            tvshows = get_tvshows(0, tvshows_count)["result"]["tvshows"]
            xbmc.log(str(json.dumps(tvshows)))
            for i in tvshows:
                if not QUITING:
                    episode_count = i["episode"]
                    episodes = get_episodes(i["tvshowid"])
                    for j in episodes["result"]["episodes"]:
                        pass
                        j["hashes"]= get_hash_array(j["file"])
                    if episode_count >= 20:
                        chunk_count = 20
                    else:
                        chunk_count = episode_count

                    for chunk in split_list(episodes["result"]["episodes"],
                                            episode_count // chunk_count):
                        # xbmc.log(str(chunk))
                        data = {
                            "event": "Library.Add",
                            "episodes": chunk
                        }
                        xbmc.log(str(json.dumps(data)))
                        # queue.add_to_queue(data)

                    # xbmc.log(str(json.dumps(episodes["result"]["episodes"])))

        if not QUITING:
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


class ApiListener(threading.Thread):
    """
    Thread that listens in the background for xbmc notifications.
    """

    def __init__(self):
        super(ApiListener, self).__init__()
        self._stop = threading.Event()
        self.sock = socket.socket()
        self.sock.settimeout(None)
        #self.sock.connect(("localhost", 9090))
        self.sock.connect(("localhost", get_api_port()))


    def process(self, data_json):
        global QUITING
        global IS_PROTECTED
        global API_LIBRARY_CACHE
        
        """
        Process notification data from xbmc.
        """
        method = data_json.get("method")

        def send_library_change(id, _type, event):
            if event == "Remove":
                if _type == "movie":
                    try_send_data({
                            "event": event,
                            "id": id,
                            "type": _type
                        }, 
                        get_token()
                    )

                elif _type == "episode":
                    try_send_data({
                            "event": event,
                            "id": id,
                            "type": _type
                        }, 
                        get_token()
                    )

            else:
                if _type == "movie":
                    details = get_movie_details(id)
                    path = details["result"]["moviedetails"]["file"]

                    if not is_protected(path):
                        if not details["result"]["moviedetails"]["imdbnumber"]:
                            details = get_movie_details(
                            data_json["params"]["data"]["item"]["id"], all_prop=True)
                        
                        details["result"]["moviedetails"]["hashes"] = get_hash_array(path)
                        try_send_data({
                                "event": event,
                                "id": id,
                                "moviedetails": details["result"]["moviedetails"],
                                "type": _type
                            },
                            get_token())

                elif _type == "episode":
                    details = get_episode_details(id)
                    path = details["result"]["episodedetails"]["file"]
                    if not is_protected(path):
                        details["result"]["episodedetails"]["hashes"] = get_hash_array(path)
                        try_send_data({
                                "event": event,
                                "id": id,
                                "episodedetails": details["result"]["episodedetails"],
                                "type": _type
                            },
                            get_token())
        
        if method == "VideoLibrary.OnRemove":
            send_library_change(
                data_json["params"]["data"]["id"], 
                data_json["params"]["data"]["type"],
                "Remove"
            )

        elif method == "VideoLibrary.OnUpdate":
            send_library_change(
                data_json["params"]["data"]["item"]["id"], 
                data_json["params"]["data"]["item"]["type"],
                "AddOrUpdate"
            )

        if method == "Player.OnStop":
            if not IS_PROTECTED:
                if data_json["params"]["data"] is not None:
                    if (data_json["params"]["data"]["item"]["type"] == "movie") and (CURRENT_TIME > 0.7 * TOTAL_TIME):
                        details = get_movie_details(data_json["params"]["data"]["item"]["id"])
                        xbmc.log(str(details))
                        ui = XMLRatingDialog("SynopsiDialog.xml", __cwd__, "Default", ctime=CURRENT_TIME,
                                             tottime=TOTAL_TIME, token=get_token(),
                                             hashd=get_hash_array(
                                                details["result"]["moviedetails"]["file"]))
                        ui.doModal()
                        del ui
                    elif (data_json["params"]["data"]["item"]["type"] == "episode") and (CURRENT_TIME > 0.7 * TOTAL_TIME):
                        details = get_episode_details(data_json["params"]["data"]["item"]["id"])
                        xbmc.log(str(details))
                        ui = XMLRatingDialog("SynopsiDialog.xml", __cwd__, "Default", ctime=CURRENT_TIME,
                                             tottime=TOTAL_TIME, token=get_token(),
                                             hashd=get_hash_array(
                                            details["result"]["episodedetails"]["file"]))
                        ui.doModal()
                        del ui


                    # TODO: Send global DATA_PACK
                    # Only onStop
                    time.sleep(1)
                    if DATA_PACK.has_key("librarydetails"):
                        del DATA_PACK["videodetails"]

                    __addon__.setSetting(id="CACHE", value=json.dumps(DATA_PACK))

        # if method == "Player.OnSeek":
        #     if not IS_PROTECTED:
        #         if data_json["params"]["data"] is not None:
        #             LIBRARY_CACHE["events"].append({
        #                 "timestamp": 1343132282.1719999,
        #                 "event": "Seek",
        #                 "currenttime": 4365.2912073401967
        #             })
        pass

    def run(self):
        global QUITING
        global IS_PROTECTED
        global API_LIBRARY_CACHE
        
        while True:
            data = self.sock.recv(1024)
            xbmc.log('At {0}: {1}'.format(time.time(), str(data)))
            try:
                data_json = json.loads(str(data))
                method = data_json.get("method")

                API_LIBRARY_CACHE = data_json.copy()
            except ValueError:
                continue

            if method == "System.OnQuit":
                QUITING = True
                break
            else:
                self.process(data_json)

        sys.exit(4)

    def __del__(self):
        self.sock.close()

    def stop(self):
        """
        Stop thread.
        """
        self.sock.close()
        self._stop.set()

    def stopped(self):
        """
        If thread is stopped.
        """
        return self._stop.isSet()


class QueueWorker(threading.Thread):
    """
    Thread that waits for signals that needs to be send or processed.
    """
    def __init__(self):
        super(QueueWorker, self).__init__()
        self.queue = []

    def run(self):
        while (not QUITING) and (not xbmc.abortRequested):
            if len(self.queue) == 0:
                xbmc.sleep(1000)
            else:
                for data in self.queue:
                    try_send_data(data, get_token())
                self.queue = []

    def add_to_queue(self, data):
        """
        Add to workers queue.
        """
        self.queue.append(data)


class XMLRatingDialog(xbmcgui.WindowXMLDialog):
    """
    Dialog class that asks user about rating of movie.
    """
    global DATA_PACK

    def __init__(self, *args, **kwargs):
        xbmcgui.WindowXMLDialog.__init__( self )
        self.data = {'event': "Dialog.Rating"}
        self.data['currenttime'] = kwargs['ctime']
        self.data['totaltime'] = kwargs['tottime']
        self.token = kwargs['token']
        self.data['hashes'] = kwargs['hashd']

    def message(self, message):
        """
        Shows xbmc dialog with OK and message.
        """
        dialog = xbmcgui.Dialog()
        dialog.ok(" My message title", message)
        self.close()

    def onInit(self):
        self.getString = __addon__.getLocalizedString
        self.getControl(11).setLabel(self.getString(69601))
        self.getControl(10).setLabel(self.getString(69602))
        self.getControl(15).setLabel(self.getString(69603))
        self.getControl(1 ).setLabel(self.getString(69604))
        self.getControl(2 ).setLabel(self.getString(69600))

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

        DATA_PACK["events"].append({
            "timestamp": time.time(),
            "event": "Rating",
            "rating": self.data['rating']
        })
        global queue
        queue.add_to_queue(self.data)
        self.close()

    def onFocus(self, controlId):
        self.controlId = controlId

    def onAction(self, action):
        if (action.getId() in CANCEL_DIALOG):
            xbmc.log("SynopsiTV: Not Rated")
            self.data['rating'] = "Not Rated"

            DATA_PACK["events"].append({
                "timestamp": time.time(),
                "event": "Rating",
                "rating": self.data['rating']
            })

            global queue
            queue.add_to_queue(self.data)
            self.close()


class SynopsiPlayer(xbmc.Player):
    """
    Inherited main player class with events.
    """
    # xbmc.log('SynopsiTV: Class player is opened')
    def __init__(self):
        xbmc.Player.__init__(self)
        # xbmc.log('SynopsiTV: Class player is initialized')
        self.hashes = {}

    def onPlayBackStarted(self):
        """
        Hook when playback starts.
        """

        if xbmc.Player().isPlayingVideo():
            xbmc.log('SynopsiTV: PLAYBACK STARTED at {0}'.format(time.time()))

            #Storing hash
            path = xbmc.Player().getPlayingFile()
            self.hashes = get_hash_array(path)
            fill_data_dict(xbmc.Player())

    def onPlayBackEnded(self):
        """
        Hook when playback ends.
        """
        global DATA_PACK
        
        DATA_PACK["events"].append({
                'event': "Ended",
                "timestamp": time.time(),
                "currenttime": CURRENT_TIME
            })

        if DATA_PACK.has_key("librarydetails"):
            ui = XMLRatingDialog("SynopsiDialog.xml", __cwd__, "Default", ctime=CURRENT_TIME,
                                                 tottime=TOTAL_TIME, token=get_token(),
                                                 hashd=[])
            ui.doModal()
            del ui
            time.sleep(1)
            if DATA_PACK.has_key("librarydetails"):
                del DATA_PACK["videodetails"]

        __addon__.setSetting(id="CACHE", value=json.dumps(DATA_PACK))

    def onPlayBackStopped(self):
        """
        Hook when playback stops.
        """
        global DATA_PACK
        
        DATA_PACK["events"].append({
                'event': "Stopped",
                "timestamp": time.time(),
                "currenttime": CURRENT_TIME
            })

        # __addon__.setSetting(id="CACHE" ,value=json.dumps(DATA_PACK))

    def onPlayBackPaused(self):
        """
        Hook when playback is paused.
        """
        global DATA_PACK

        if xbmc.Player().isPlayingVideo():
            xbmc.log('SynopsiTV: PLAYBACK PAUSED')
            send_player_status(xbmc.Player(), 'Player.Paused')

            DATA_PACK["events"].append({
                'event': "Paused",
                "timestamp": time.time(),
                "currenttime": CURRENT_TIME
            })

    def onPlayBackResumed(self):
        """
        Hook when playback is resumed.
        """
        global DATA_PACK
        if xbmc.Player().isPlayingVideo():
            xbmc.log('SynopsiTV: PLAYBACK RESUMED')
            send_player_status(xbmc.Player(), 'Player.Resumed')

            DATA_PACK["events"].append({
                'event': "Resumed",
                "timestamp": time.time(),
                "currenttime": CURRENT_TIME
            })


PLAYER = SynopsiPlayer()
QUITING = False
LOGIN_FAILED = False
CURRENT_TIME = 0
TOTAL_TIME = 0
VIDEO = 0
IS_PROTECTED = False
queue = QueueWorker()
queue.start()
DATA_PACK = {}
API_LIBRARY_CACHE = {}
LIBRARY_CACHE = get_library_cache()

def main():
    global VIDEO
    global CURRENT_TIME
    global TOTAL_TIME
    global IS_PROTECTED

    xbmc.log('SynopsiTV: Addon information')
    xbmc.log('SynopsiTV: ----> Addon name    : ' + __addonname__)
    xbmc.log('SynopsiTV: ----> Addon path    : ' + __cwd__)
    xbmc.log('SynopsiTV: ----> Addon author  : ' + __author__)
    xbmc.log('SynopsiTV: ----> Addon version : ' + __version__)

    xbmc.log('SynopsiTV: STARTUP')
    notification("SynopsiTV", "STARTUP")

    if __addon__.getSetting("BOOLTOK") == "false":
        notification("SynopsiTV", "Opening Settings")
        __addon__.openSettings()

    # __addon__.openSettings()

    xbmc.log(__cwd__)

    check_send_queue()

    if __addon__.getSetting("FIRSTRUN") == "true":
        search_thread = Searcher()
        search_thread.start()

    thr = ApiListener()
    thr.start()

    # notify_all()

    # xbmc.executebuiltin('Skin.SetString(SynopsiTV,31323)')
    while (not xbmc.abortRequested):

        if xbmc.Player().isPlayingVideo():
            VIDEO = 1
            CURRENT_TIME = xbmc.Player().getTime()
            TOTAL_TIME = xbmc.Player().getTotalTime()
            if is_protected(xbmc.Player().getPlayingFile()):
                IS_PROTECTED = True
            else:
                IS_PROTECTED = False
        else:
            VIDEO = 0
            IS_PROTECTED = False

        if (
            (__addon__.getSetting("BOOLTOK") == "false") and
            (__addon__.getSetting("USER") != "") and
            (__addon__.getSetting("PASS") != "")
            ):
            if not LOGIN_FAILED:
                xbmc.log("SynopsiTV: Trying to login")
                login(__addon__.getSetting("USER"),
                      __addon__.getSetting("PASS"))

        xbmc.sleep(1000)


    if (xbmc.abortRequested):
        if not thr.stopped:
            thr.stop()
        del thr


        xbmc.log('SynopsiTV: Aborting...')
        sys.exit(4)


if __name__ == "__main__":
    main()
