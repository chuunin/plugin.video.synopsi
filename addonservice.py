# python standart lib
import mythread
import traceback
import SocketServer

# application
from addonutilities import *

class ServiceTCPHandler(SocketServer.BaseRequestHandler):
	def __init__(self, *args, **kwargs):
		SocketServer.BaseRequestHandler.__init__(self, *args, **kwargs)		
			
	def handle(self):
		self._log = self.server._log
		
		# self.request is the TCP socket connected to the client
		self.data = self.request.recv(1024).strip()		
		
		# parse data
		try:
			json_data = json.loads(self.data)
		except:
			self._log.debug('Invalid data "%s"' % str(self.data))
			return

		try:
			# handle requested method
			methodName = json_data['command']
			arguments = json_data.get('arguments', {})

			method = getattr(self, methodName)
			result = method(arguments)
			
			# convert non-string result to json string
			if not isinstance(result, str):
				result = json.dumps(result)
				
			self.request.sendall(result)
			
		except Exception as e:
			# raise
			self._log.error('ERROR CALLING METHOD "%s": %s' % (methodName, str(e)))
			self._log.error('TRACEBACK / ' + traceback.format_exc())


# handler methods
class AddonHandler(ServiceTCPHandler):
	def get_global_recco(self, arguments):
		self._log.debug(dump(arguments))
		#~ return self._get_global_recco(**arguments)
		return self._get_global_recco(**arguments)

	def _get_global_recco(self, movie_type):
		resRecco = self.server.apiClient.profileRecco(movie_type, False, reccoDefaulLimit, reccoDefaultProps)

		# log('global recco for ' + movie_type)
		# for title in resRecco['titles']:
		#	log(title['name'])

		return resRecco

class AddonService(mythread.MyThread):	
	def __init__(self, host, port, apiClient):
		super(AddonService, self).__init__()
		self.host = host		# Symbolic name meaning all available interfaces
		self.port = port		# Arbitrary non-privileged port
		self.apiClient = apiClient
		self.server = None

	def run(self):
		self._log.debug('ADDON SERVICE / Thread start')
		
		# Create the server
		self.server = SocketServer.TCPServer((self.host, self.port), AddonHandler)
		self.server.apiClient = self.apiClient
		self.server._log = self._log
		self.server.serve_forever()

		self._log.debug('ADDON SERVICE / Thread end')

	def stop(self):
		self._log.debug('ADDON SERVICE / Shutdown start')
		self.server.shutdown()
		self._log.debug('ADDON SERVICE / Shutdown end')

