# python standart lib
import mythread
import traceback
import SocketServer

# application
from addonutilities import *

class ServiceTCPHandler(SocketServer.BaseRequestHandler):
	def handle(self):
		# self.request is the TCP socket connected to the client
		self.data = self.request.recv(1024).strip()
		log("{} wrote:".format(self.client_address[0]))
		log(dump(self.data))
		
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
			self.request.sendall(result)
			
		except Exception as e:
			# raise
			log('ERROR CALLING METHOD "%s": %s' % (methodName, str(e)))
			log('TRACEBACK / ' + traceback.format_exc())

class AddonService(mythread.MyThread):	
	def __init__(self, host, port, apiClient):
		super(AddonService, self).__init__()
		self.host = host		# Symbolic name meaning all available interfaces
		self.port = port		# Arbitrary non-privileged port
		self.apiClient = apiClient

	def run(self):
		self._log.debug('ADDON SERVICE / Thread start')
		
		# Create the server
		self.server = SocketServer.TCPServer((self.host, self.port), ServiceTCPHandler)
		self.server.serve_forever()

		self._log.debug('ADDON SERVICE / Thread end')

	def stop(self):
		self._log.debug('ADDON SERVICE / Shutdown start')
		self.server.shutdown()
		self._log.debug('ADDON SERVICE / Shutdown end')

	# handler methods
	def get_items(self, arguments):
		return get_items(self.apiClient, **arguments)

