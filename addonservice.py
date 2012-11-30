# python standart lib
import mythread
import traceback
import SocketServer
import thread

# application
from addonutilities import *
from utilities import *

class ServiceTCPHandler(SocketServer.StreamRequestHandler):
	def __init__(self, *args, **kwargs):
		SocketServer.StreamRequestHandler.__init__(self, *args, **kwargs)

	def handle(self):
		# self.request is the TCP socket connected to the client

		self.data = self.rfile.readline()

		# parse data
		try:
			json_data = json.loads(self.data)
		except:
			self.server._log.debug('Invalid data "%s"' % str(self.data))
			return

		try:
			# handle requested method
			methodName = json_data['command']
			arguments = json_data.get('arguments', {})

			method = getattr(self, methodName)
			result = method(**arguments)

			# convert non-string result to json string
			if not isinstance(result, str):
				result = json.dumps(result)
			elif not result:
				result = '{}'

			self.server._log.debug('RESULT: ' + result)

			self.wfile.write(result)

		except Exception as e:
			# raise
			self.server._log.error('ERROR CALLING METHOD "%s": %s' % (methodName, str(e)))
			self.server._log.error('TRACEBACK / ' + traceback.format_exc())


# handler methods
class AddonHandler(ServiceTCPHandler):
	def get_global_recco(self, movie_type):
		resRecco = self.server.apiClient.profileRecco(movie_type, False, reccoDefaulLimit, reccoDefaultProps)

		# log('global recco for ' + movie_type)
		# for title in resRecco['titles']:
		#	log(title['name'])

		return resRecco

	def get_tvshows(self):
		result = []
		result += self.get_local_tvshows()
		result += self.get_top_tvshows()

		return result

	def get_local_tvshows(self):
		local_tvshows = self.server.stvList.getAllByType('tvshow')
		return local_tvshows.values()

	def get_top_tvshows(self):
		episodes = self.server.apiClient.unwatchedEpisodes()

		# log('top tvshows')
		# for title in episodes['top']:
		#	 log(title['name'])

		result = episodes['top']
		return result


	def get_local_recco(self, movie_type):
		resRecco = self.server.apiClient.profileRecco(movie_type, True, reccoDefaulLimit, reccoDefaultProps)

		# log('local recco for ' + movie_type)
		# for title in resRecco['titles']:
		#	log('resRecco:' + title['name'])

		return resRecco

	def get_local_recco2(self, movie_type):
		""" Updates the get_local_recco function result to include stv_title_hash """
		recco = self.get_local_recco(movie_type)['titles']

		for title in recco:
			if self.server.stvList.hasStvId(title['id']):
				cached_title = self.server.stvList.getByStvId(title['id'])
				log('found in cache:' + dump(cached_title))
				title['stv_title_hash'] = cached_title['stv_title_hash']
				title['file'] = cached_title['file']

		return recco

	def get_unwatched_episodes(self):
		return self.server.apiClient.get_unwatched_episodes()

	def get_upcoming_episodes(self):
		return self.server.apiClient.get_upcoming_episodes()

	def get_tvshow_season(self, tvshow_id):
		season = self.server.apiClient.season(tvshow_id)
		return season['episodes']

	def get_title(self, stv_id, detailProps=defaultDetailProps, castProps=defaultCastProps):
		return self.server.apiClient.title(stv_id, detailProps, castProps)

	def get_title_similars(self, stv_id):
		self.server.apiClient.titleSimilar(stv_id)

	def get_tvshow(self, stv_id, **kwargs):
		return self.server.apiClient.tvshow(stv_id, **kwargs)

	def show_video_dialog(self, json_data):
		thread.start_new_thread(show_video_dialog, (json_data, self.server.apiClient, self.server.stvList))

	def show_video_dialog_byId(self, stv_id):
		thread.start_new_thread(show_video_dialog_byId, (stv_id, self.server.apiClient, self.server.stvList))

	def open_settings(self):
		__addon__ = get_current_addon()
		thread.start_new_thread(__addon__.openSettings, ())

	def debug_1(self):
		self.server.stvList.clear()
		episode = {
			'tvshow_id': 14335,
			'type': 'episode',
			'id': 22835,
			'name': 'Something Blue',
			'file': '/media/sdb1/blah blah.avi'
		}

		self.server.stvList.put(episode)
		self.server.stvList.add_tvshow(1, 14335)
		self.server.stvList.list()

	def debug_2(self):
		self.server.stvList.list()

	def debug_3(self):
		log(dump(self.server.stvList.byStvId))


class AddonServer(SocketServer.TCPServer):
	allow_reuse_address = True
	def __init__(self, host, port):
		SocketServer.TCPServer.__init__(self, (host, port), AddonHandler)


class AddonService(mythread.MyThread):
	def __init__(self, host, port, apiClient, stvList):
		super(AddonService, self).__init__()
		self.host = host		# Symbolic name meaning all available interfaces
		self.port = port		# Arbitrary non-privileged port

		self.server = AddonServer(self.host, self.port)
		self.server.apiClient = apiClient
		self.server.stvList = stvList


	def run(self):
		self._log.debug('ADDON SERVICE / Thread start')

		# Create the server
		self.server._log = self._log
		self.server.serve_forever()

		self._log.debug('ADDON SERVICE / Thread end')

	def stop(self):
		self.server.shutdown()

