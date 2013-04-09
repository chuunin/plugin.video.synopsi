

# python standart lib
import sys
import json
import urlparse
import traceback
import random
from lxml.builder import E
from lxml import etree
import BaseHTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
from mythread import MyThread
from httplib2 import Http

# application
from utilities import *
import top
from apiclient import ApiClient


class ScraperServer(BaseHTTPServer.HTTPServer):
	def __init__(self, server_address):
		BaseHTTPServer.HTTPServer.__init__(self, server_address, ScraperRequestHandler)

class ScraperRequestHandler(SimpleHTTPRequestHandler):
	protocol_version = "HTTP/1.0"

	def log(self, msg):
		log('SCRAPER: ' + unicode(msg))

	def do_GET(self):
		try:
			url = urlparse.urlparse(self.path)
			qs = urlparse.parse_qs(url.query)
			
			str_response = 'Unhandled'

			if url.path == '/search/':
				str_response = self.path_search(url, qs)
			elif url.path == '/get_detail/':
				str_response = self.path_get_detail(url, qs)

		except:
			exc_type, exc_value, exc_traceback = sys.exc_info()
			exc_string = traceback.extract_tb(exc_traceback)
			# exc_string = traceback.format_exception(exc_type, exc_value, exc_traceback)
			response = {'status': 'exception', 'exc_type': str(exc_type), 'exc_value': str(exc_value), 'traceback': exc_string}
			str_response = json.dumps(response)

		self.log(self.path)
		self.log(str_response)

		self.wfile.write(str_response)
		self.wfile.write('\n')

	def title_identify(self, file_name, type):
		movie = {}
		movie['file'] = file_name

		path = self.get_path(movie)
		# DISABLED while testing
		# movie['stv_title_hash'] = stv_hash(path)
		# movie['os_title_hash'] = hash_opensubtitle(path)
		
		# TODO: stv_subtitle_hash - hash of the subtitle file if present
		ident = {}
		self._translate_xbmc2stv_keys(ident, movie)

		# give api a hint about type if possible
		if movie['type'] in playable_types:
			ident['type'] = movie['type']

		# correct input
		if ident.get('imdb_id'):
			ident['imdb_id'] = ident['imdb_id'][2:]

		# try to get synopsi id
		log('to identify: ' + ident['file_name'])
		title = top.apiClient.titleIdentify(**ident)
		return title

	def path_search(self, url, qs):
		if not qs.get('q'):
			raise Exception('Missing parameter: q')

		file_name = qs['q'][0]

		self.send_response(200)
		self.send_header("Content-type", "text/xml")
		self.end_headers()


		title = self.title_identify(self, qs['q'])
		# title = {'id': str(random.randint(1,1000))}
		
		print 'storing cache id: ' + str(title['id'])
		self.server.cache[title['id']] = title

		xml_root = E.results(
			E.title(
				E.id( title['id'] ),
			)
		)

		str_response = etree.tostring(xml_root, pretty_print=True)

		return str_response

	def path_get_detail(self, url, qs):
		stv_id = qs.get('q')[0]

		t = title = self.server.cache[stv_id]

		log(dump(t))
		
		# t = {
		# 	'name': 'Fake Name' + stv_id, 
		# 	'year': 2010, 
		# 	'directors': 'Fake Directors',
		# 	'runtime': '20 min',
		# 	'genres': 'Fake Comedy',
		# 	'plot': 'Codem checksum'
		# }

		return '''
				<title>%s</title>
				<year>%s</year>
				<director>%s</director>
				<top250></top250>
				<mpaa></mpaa>
				<tagline></tagline>
				<runtime>%s</runtime>
				<thumb></thumb>
				<credits></credits>
				<rating></rating>
				<votes></votes>
				<genre>%s</genre>
				<actor>
					<name></name>
					<role></role>
				</actor>
				<outline></outline>
				<plot>%s</plot>
			''' % (t['name'], t['year'], t['directors'], t['runtime'], t['genres'], t['plot'])


class ScraperServerThread(ScraperServer, MyThread):
	_stopped = False
	cache = {}

	def __init__(self, server_address):
		ScraperServer.__init__(self, server_address)
		MyThread.__init__(self)

	def serve_forever(self):
		while not self._stopped:
			self.handle_request()

	def run(self):
		log('starting server')
		self.serve_forever()
		log('stopping server')

	def server_stop(self):
		self._stopped = True
		self.create_dummy_request()
		self.server_close()

	def create_dummy_request(self):
		h = Http()
		h.request('http://%s:%s' % self.server_address, "HEAD")

if __name__ == '__main__':

	top.apiClient = ApiClient.getDefaultClient()

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
