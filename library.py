# xbmc
import xbmc, xbmcgui, xbmcaddon

# python standart library
import time
import socket
import json
import re
import traceback
import top

# application
from mythread import MyThread
from utilities import *
from cache import *


ABORT_REQUESTED = False


class RPCListener(MyThread):
	def __init__(self, cache):
		super(RPCListener, self).__init__()

		self.cache = cache
		self.sock = socket.socket()
		self.sock.settimeout(5)
		self.connected = False
		self._stop = False
		sleepTime = 100
		t = time.time()
		port = get_api_port()
		while sleepTime<500 and (not self.connected or ABORT_REQUESTED or xbmc.abortRequested):
			try:
				self.sock.connect(("localhost", port))
			except Exception, exc:
				log('%0.2f %s' % (time.time() - t, str(exc)))
				xbmc.sleep(int(sleepTime))
				sleepTime *= 1.5
			else:
				self._log.info('Connected to %d' % port)
				self.connected = True

		self.sock.setblocking(True)

	def process(self, data):
		pass

	def run(self):
		global ABORT_REQUESTED

		if not self.connected:
			self._log.error('RPC Listener cannot run, there is not connection to xbmc')
			return False

		while not self._stop:
			data = ''
			while not self._stop:
				if not data:
					# self._log.debug('first read')
					chunk = self.sock.recv(1024)	
				else:
					# self._log.debug('continued read')
					self.sock.setblocking(False)
					try:
						chunk = self.sock.recv(1024)	
					except Exception as e:
						# we are here = didn't recv anything
						chunk = None
					# self._log.debug('read: ' + str(chunk))

				if not chunk:
					self.sock.setblocking(True)
					break

				data += chunk
				# self._log.debug('recv ' + str(chunk))
			
			# self._log.debug('recvd data:' + str(data))
			data = data.replace('}{', '},{')
			datapack = '[%s]' % data
			
			try:
				data_json = json.loads(datapack)
			except ValueError, e:
				self._log.error('RPC ERROR:' + unicode(e))
				self._log.error('RPC ERROR DATA:' + unicode(data))
				continue

			for request in data_json:
				method = request.get("method")

				if method == "System.OnQuit":
					self._stop = True
					ABORT_REQUESTED = True
					break
				else:
					self.process(request)

		self.sock.close()
		self._log.info('Library thread end')

	def process(self, data):
		methodName = data['method'].replace('.', '_')
		method = getattr(self, methodName, None)
		if method == None:
			self._log.warn('Unknown method: ' + methodName)
			return

		self._log.debug(str(data))

		#   Try to call that method
		try:
			method(data)
		except:
			self._log.error('Error in method "' + methodName + '"')
			self._log.error(traceback.format_exc())

		#   http://wiki.xbmc.org/index.php?title=JSON-RPC_API/v4


class RPCListenerHandler(RPCListener):
	"""
	RPCListenerHandler defines event handler methods that are autotically called from parent class's RPCListener
	"""
	def __init__(self, cache):
		super(RPCListenerHandler, self).__init__(cache)

	def _xbmc_time2sec(self, time):
		return time["hours"] * 3600 + time["minutes"] * 60 + time["seconds"] + time["milliseconds"] / 1000

	#   NOT USED NOW
	def playerEvent(self, data):
		self._log.debug(dump(data))

	def VideoLibrary_OnUpdate(self, data):
		i = data['params']['data']['item']

		self.scraper_addorupdate(i['type'], i['id'])

	def VideoLibrary_OnRemove(self, data):
		d = data['params']['data']

	def Player_OnPlay(self, data):
		pass

	def Player_OnStop(self, data):
		pass

	def Player_OnSeek(self, data):
		pass

	def Player_OnPause(self, data):
		pass

	def Player_OnResume(self, data):
		pass

	def GUI_OnScreenSaverActivated(self, data):
		pass

	def GUI_OnScreenSaverDeactivated(self, data):
		pass


	def scraper_addorupdate(self, atype, aid):
		if atype != 'movie':
			return

		movie = xbmc_rpc.get_movie_details(aid)
		movie['type'] = atype
		movie['id'] = aid
		
		log('LIBRARY_ADD_UPDATE: %s--%s [%s]' % (movie['type'], movie['id'], movie['file']))

		if movie['title'] == 'N/A':
			path = get_movie_path(movie)
			movie['stv_title_hash'] = stv_hash(path)
			movie['os_title_hash'] = hash_opensubtitle(path)

			# TODO: stv_subtitle_hash - hash of the subtitle file if present
			ident = {}
			translate_xbmc2stv_keys(ident, movie)

			# give api a hint about type if possible
			if movie['type'] in playable_types:
				ident['type'] = movie['type']

			# try to get synopsi id
			self._log.info('to identify: ' + ident['file_name'])
			title = top.apiClient.titleIdentify(**ident)

			# if identified			
			if title.has_key('id'):
				movie['stvId'] = title['id']
				self._log.info('identified: ' + title['name'])
				
				##+ scraper part
				details = copy(title)
				details['id'] = movie['id']
				if details.has_key('relevant_results'):
					del(details['relevant_results'])

				# self._log.debug('details:' + dump(details))
				
				filtered_details = translate_stv2xbmc(details)

				# self._log.debug('filtered_details:' + dump(filtered_details))
				
				xbmc_rpc.set_movie_details(filtered_details)
				##- scraper part
			# if identification failed
			else:
				self._log.info('NOT identified %s' % movie['file'])
