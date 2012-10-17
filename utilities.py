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
import uuid
from base64 import b64encode
from urllib import urlencode
from urllib2 import Request, urlopen


CANCEL_DIALOG = (9, 10, 92, 216, 247, 257, 275, 61467, 61448, )
CANCEL_DIALOG2 = (61467, )


__addon__    = xbmcaddon.Addon()
__cwd__      = __addon__.getAddonInfo('path')



class XMLRatingDialog(xbmcgui.WindowXMLDialog):
	"""
	Dialog class that asks user about rating of movie.
	"""
	response = 4
	# 1 = Amazing, 2 = OK, 3 = Terrible, 4 = Not rated
	def __init__(self, *args, **kwargs):
		xbmcgui.WindowXMLDialog.__init__( self )
 
	def onInit(self):
		self.getString = __addon__.getLocalizedString
		self.getControl(11).setLabel(self.getString(69601))
		self.getControl(10).setLabel(self.getString(69602))
		self.getControl(15).setLabel(self.getString(69603))
		self.getControl(1 ).setLabel(self.getString(69604))
		self.getControl(2 ).setLabel(self.getString(69600))

	def onClick(self, controlId):
		"""
		For controlID see: <control id="11" type="button"> in SynopsiDialog.xml
		"""
		if controlId == 11:
			self.response = 1
		elif controlId == 10:
			self.response = 2
		elif controlId == 15:
			self.response = 3
		else:
			self.response = 4
		self.close()

	def onAction(self, action):
		if (action.getId() in CANCEL_DIALOG):
			self.response = 4
			self.close()

class XMLLoginDialog(xbmcgui.WindowXMLDialog):
	"""
	Dialog class that asks user about rating of movie.
	"""
	response = 4
	# 1 = Cancel, 2 = OK
	def __init__(self, *args, **kwargs):
		xbmcgui.WindowXMLDialog.__init__( self )
		self.username = kwargs['username']
		self.password = kwargs['password']
 
	def onInit(self):
		self.getString = __addon__.getLocalizedString
		c = self.getControl(10)
		
		for i in dir(c):
			xbmc.log('control item:' + str(i))

		self.getControl(10).setText(self.username)
		self.getControl(11).setText(self.password)

	def onClick(self, controlId):
		"""
		For controlID see: <control id="11" type="button"> in SynopsiDialog.xml
		"""
		xbmc.log(str('onClick:'+str(controlId)))

		# Cancel
		if controlId==16:
			self.response = 1
			self.close()
		# Ok
		elif controlId==15:
			self.response = 2
			self.close()

	def onAction(self, action):
		xbmc.log('action id:' + str(action.getId()))
		if (action.getId() in CANCEL_DIALOG2):
			self.response = 1
			self.close()

	def getData(self):
		return { 'username': self.getControl(10).getText(), 'password': self.getControl(11).getText() }



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
	sha1.update(xbmcBuildVer)
	return sha1.hexdigest()

def generate_iuid():
	"""
	Returns install-uniqe id. Has to be generated for every install.
	"""
	
	return str(uuid.uuid1())



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

def XBMC_GetInfoLabels():
	"""
	"""

	response = xbmcRPC.execute(
		'XBMC.GetInfoLabels',
		{
			'properties' : [ 'System.CpuFrequency', 'System.KernelVersion','System.FriendlyName','System.BuildDate','System.BuildVersion' ]
		}
	)

	return response


def get_details(atype, aid, all_prop=False):
	if atype == "movie":                
		movie = get_movie_details(aid, all_prop)
	elif atype == "episode":
		movie = get_episode_details(aid, all_prop)
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
		
		json_response = json.loads(response)

		if self.__logLevel:
			xbmc.log('xbmc RPC response: ' + str(json.dumps(json_response, indent=4)))

		if json_response.has_key('error') and json_response['error']:
			raise Exception(json_response['error']['message'])

		return json_response['result']

def get_install_id():
	global __addon__
	
	iuid = __addon__.getSetting(id='INSTALL_UID')
	if not iuid:
		iuid = generate_iuid()
		xbmc.log('iuid:' + iuid)
		__addon__.setSetting(id='INSTALL_UID', value=iuid)

	return iuid

def home_screen_fill(apiClient):
	"""
	This method updates movies on HomePage.
	"""

	# get recco movies and episodes
	movie_recco = apiClient.profileRecco('movie')['titles']
	episode_recco = apiClient.profileRecco('episode')['titles']

	# from test import jsfile
	# movie_recco = jsfile
	# episode_recco = jsfile

	# xbmc.log('movie_recco:' + json.dumps(movie_recco, indent=4))
	# xbmc.log('episode_recco:' + json.dumps(episode_recco, indent=4))
	xbmc.log('movie_recco count:' + str(len(movie_recco)))
	xbmc.log('episode_recco count:' + str(len(episode_recco)))

	WINDOW = xbmcgui.Window( 10000 )
	MOVIES_COUNT = 5
	
	for i in range(1, MOVIES_COUNT+1):
		m = movie_recco[i]
		xbmc.log('movie %d %s' % (i, m['name']))
		WINDOW.setProperty("LatestMovie.{0}.Title".format(i), m['name'])
		WINDOW.setProperty("LatestMovie.{0}.Path".format(i), m['cover_large'])
		WINDOW.setProperty("LatestMovie.{0}.Thumb".format(i), m['cover_thumbnail'])
		WINDOW.setProperty("LatestMovie.{0}.Fanart".format(i), m['cover_large'])

		e = episode_recco[i]
		xbmc.log('episode %d %s' % (i, e['name']))
		WINDOW.setProperty("LatestEpisode.{0}.EpisodeTitle".format(i), e['name'])
		WINDOW.setProperty("LatestEpisode.{0}.ShowTitle".format(i), e['name'])
		WINDOW.setProperty("LatestEpisode.{0}.EpisodeNo".format(i), str(i))
		WINDOW.setProperty("LatestEpisode.{0}.Path".format(i), e['cover_large'])
		WINDOW.setProperty("LatestEpisode.{0}.Thumb".format(i), e['cover_large'])
		WINDOW.setProperty("LatestEpisode.{0}.Fanart".format(i), e['cover_thumbnail'])

def login_screen():
	username = __addon__.getSetting('USER')
	password = __addon__.getSetting('PASS')

	ui = XMLLoginDialog("LoginDialog.xml", __cwd__, "Default", username=username, password=password)
	ui.doModal()
	
	# dialog result is 'OK'
	if ui.response==2:
		# check if data changed
		d = ui.getData()
		if username!=d['username'] or password!=d['password']:
			# store in settings
			__addon__.setSetting('USER', value=d['username'])
			__addon__.setSetting('PASS', value=d['password'])
			result=True
		else:
			result=False
	else:
		result=False
	
	del ui
	return result

def get_rating():
	"""
	Get rating from user:
	1 = Amazing, 2 = OK, 3 = Terrible, 4 = Not rated
	"""
	ui = XMLRatingDialog("SynopsiDialog.xml", __cwd__, "Default")
	ui.doModal()
	_response = ui.response
	del ui
	return _response


# init local variables
xbmcRPC = xbmcRPCclient(1)
