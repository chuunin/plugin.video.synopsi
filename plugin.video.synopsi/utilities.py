try:
    import xbmc, xbmcgui, xbmcaddon
except ImportError:
    from tests import xbmc, xbmcgui, xbmcaddon
import json
import struct
import os
import urllib
import urlparse
import hashlib

from base64 import b64encode
from urllib import urlencode
from urllib2 import Request, urlopen

# definitions of properties
KEY = 'd0198f911ef0292c83850f9dd77a5a'
SECRET = '69884a55080284e41937e7a007e522'

HTTP_HEADERS = {
            'AUTHORIZATION': 'BASIC %s' % b64encode("%s:%s" % (KEY, SECRET)),
            'user-agent': 'linux'
}
__addon__     = xbmcaddon.Addon()



def get_token(user, passwd):
    """
    Get oauth token.
    """
    data = {
    'grant_type':'password',
    'client_id': KEY,
    'client_secret': SECRET,
    'username': user,
    'password': passwd
    }
    response = urlopen(Request('http://dev.synopsi.tv/oauth2/token/', 
        data=urlencode(data), 
        headers=HTTP_HEADERS, origin_req_host='dev.synopsi.tv'
    ))
    response_json = json.loads(response.readline())
    access_token = response_json['access_token']
    # refresh_token = response_json['refresh_token']
    # Permanent token
    # return (access_token, refresh_token)

    return (access_token, "")


def send_data(json_data, access_token):
    """
    Send data.
    """
    # example of sending data
    # json_data = {'test': 'example'}
    data = {
    'client_id': KEY,
    'client_secret': SECRET,
    'bearer_token': access_token,
    'data': json.dumps(json_data)
    }
    
    # response = urlopen(Request('http://dev.synopsi.tv/api/desktop/',
    #     data=urlencode(data),
    #     headers=HTTP_HEADERS, origin_req_host='dev.synopsi.tv'
    # ))
    response = urlopen(Request('http://localhost/',
        data=urlencode(data),
        headers=HTTP_HEADERS, origin_req_host='dev.synopsi.tv'
    ))


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


def stv_hash(filepath):
    """
    New synopsi hash. Inspired by sutitle hash using first 
    and last 64 Kbytes and length in bytes.
    """

    sha1 = hashlib.sha1()

    try:
        with open(filepath, 'rb') as f:
            sha1.update(f.read(65536))
            f.seek(-65536, 2)
            sha1.update(f.read(65536))
        sha1.update(str(os.path.getsize(filepath)))
    except (IOError) as e:
        return None
    
    return sha1.hexdigest()


def old_stv_hash(filepath):
    """
    Old synopsi hash. Using only first and last 256 bytes.   
    """

    sha1 = hashlib.sha1()

    try:
        with open(filepath, 'rb') as f:
            sha1.update(f.read(256))
            f.seek(-256, 2)
            sha1.update(f.read(256))
    except (IOError) as e:
        return None
    
    return sha1.hexdigest()


def hashFile(name):
    """
    OpenSubtitles hash.
    """
    try:
        longlongformat = 'q'  # long long 
        bytesize = struct.calcsize(longlongformat) 
         
        _file = open(name, "rb")
              
        filesize = os.path.getsize(name) 
        hash = filesize
              
        if filesize < 65536 * 2:
            return None
            # return "SizeError" 
             
        for x in range(65536 / bytesize): 
            _buffer = _file.read(bytesize) 
            (l_value,) = struct.unpack(longlongformat, _buffer)  
            hash += l_value 
            hash = hash & 0xFFFFFFFFFFFFFFFF #to remain as 64bit number  

        _file.seek(max(0, filesize - 65536), 0)
        for x in range(65536 / bytesize):
            _buffer = _file.read(bytesize) 
            (l_value,)= struct.unpack(longlongformat, _buffer)  
            hash += l_value 
            hash = hash & 0xFFFFFFFFFFFFFFFF 

        _file.close()
        returnedhash =  "%016x" % hash 
        
        return returnedhash 

    except(IOError):
        return None
        # return "IOError"


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
    #TODO
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

    response = xbmcRPC.execute(
        'VideoLibrary.GetMovies',
        {
            'properties': properties,
            'limits': {'end': end, 'start': start}
        }
    )

    return response


def get_all_movies():
    """
    Get movies from xbmc library. Start is the first in list and end is the last.
    """
    properties = ['file', 'imdbnumber', "lastplayed", "playcount"]

    response = xbmcRPC.execute(
        'VideoLibrary.GetMovies',
        {
            'properties': properties
        }
    )

    return response

def get_all_tvshows():
    """
    Get movies from xbmc library. Start is the first in list and end is the last.
    """
    properties = ['file', 'imdbnumber', "lastplayed", "playcount", "episode"]

    response = xbmcRPC.execute(
        'VideoLibrary.GetTVShows',
        {
            'properties': properties
        }
    )

    return response

def get_tvshows(start, end):
    """
    Get movies from xbmc library. Start is the first in list and end is the last.
    """
    properties = ['file', 'imdbnumber', "lastplayed", "playcount", "episode"]

    response = xbmcRPC.execute(
        'VideoLibrary.GetTVShows',
        {
            'properties': properties,
            'limits': {'end': end, 'start': start}
        }
    )

    return response


def get_episodes(twshow_id, season=-1):
    """
    Get episodes from xbmc library.
    """
    properties = ['file', "lastplayed", "playcount", "season", "episode"]
    if season == -1:
        params = {
            'properties': properties,
            'tvshowid': twshow_id
        }
    else:
        params = {
            'properties': properties,
            'tvshowid': twshow_id,
            'season': season
        }

    response = xbmcRPC.execute(
        'VideoLibrary.GetEpisodes',
        params
    )

    return response

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

    response = xbmcRPC.execute(
        'VideoLibrary.GetMovieDetails',
        {
            'properties': properties,
            'movieid': movie_id  # s 1 e 2 writes 2
        }
    )

    return response['moviedetails']


def get_tvshow_details(movie_id):
    """
    Get dict of movie_id details.
    """
    properties = ['file', 'imdbnumber', "lastplayed", "playcount"]

    response = xbmcRPC.execute(
        'VideoLibrary.GetTVShowDetails',
        {
            'properties': properties,
            'movieid': movie_id  # s 1 e 2 writes 2
        }
    )

    return response


def get_episode_details(movie_id):
    """
    Get dict of movie_id details.
    """
    properties = ['file', "lastplayed", "playcount", "season", "episode", "tvshowid"]

    response = xbmcRPC.execute(
        'VideoLibrary.GetEpisodeDetails',
        {
            'properties': properties,
            'episodeid': movie_id
        }
    )

    return response['episodedetails']

def get_details(atype, aid):
    if atype == "movie":                
        movie = get_movie_details(aid)
    elif atype == "episode":
        movie = get_episode_details(aid)
    return movie

class xbmcRPCclient(object):

    def __init__(self, logLevel = 0):
        self.__logLevel = logLevel

    def execute(self, methodName, params):
        dic = {
            'params': params,
            'jsonrpc': '2.0',
            'method': methodName,
            'id': 1
        }

        if self.__logLevel:
            xbmc.log('xbmc RPC request: ' + str(json.dumps(dic)))

        response = xbmc.executeJSONRPC(json.dumps(dic))
        
        if self.__logLevel:
            xbmc.log('xbmc RPC response: ' + str(response))

        return json.loads(response)['result']

xbmcRPC = xbmcRPCclient(1)

