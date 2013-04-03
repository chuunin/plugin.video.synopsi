

# python standart lib
import sys
import json
import urlparse
import traceback
import BaseHTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
from threading import Thread
from httplib2 import Http


class ScraperServer(BaseHTTPServer.HTTPServer):
	def __init__(self, server_address):
		BaseHTTPServer.HTTPServer.__init__(self, server_address, ScraperRequestHandler)

class ScraperRequestHandler(SimpleHTTPRequestHandler):
	protocol_version = "HTTP/1.0"


	def do_GET(s):
		try:
			url = urlparse.urlparse(s.path)
			qs = urlparse.parse_qs(url.query)
			file_name = qs['q'][0]

			s.send_response(200)
			s.send_header("Content-type", "text/json")
			s.end_headers()

			response = {}
			response['requested'] = file_name
		except:
			exc_type, exc_value, exc_traceback = sys.exc_info()
			response = {'status': 'exception', 'traceback': traceback.extract_tb(exc_traceback)}

		s.wfile.write(json.dumps(response))
		s.wfile.write('\n')

class ScraperServerThread(ScraperServer, Thread):
	_stopped = False

	def __init__(self, server_address):
		ScraperServer.__init__(self, server_address)
		Thread.__init__(self)

	def serve_forever(self):
		while not self._stopped:
			self.handle_request()

	def run(self):
		self.serve_forever()

	def server_stop(self):
		self._stopped = True
		self.create_dummy_request()
		self.server_close()

	def create_dummy_request(self):
		h = Http()
		h.request('http://%s:%s' % self.server_address, "HEAD")

if __name__ == '__main__':
	server_address = ('127.0.0.1', 9099)
	scraper_server_thread = ScraperServerThread(server_address)
	scraper_server_thread.start()

	print 'Scraper Server is running'
	# scraper_server_thread.join(0.2)
	try:
		while 1:
			pass
	except KeyboardInterrupt:
		scraper_server_thread.server_stop()
