

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
from httplib2 import Http

# application
from mythread import MyThread
from loggable import Loggable
from utilities import *
import top
from apiclient import ApiClient


class ScraperServer(BaseHTTPServer.HTTPServer):
	def __init__(self, server_address):
		BaseHTTPServer.HTTPServer.__init__(self, server_address, ScraperRequestHandler)

class ScraperRequestHandler(SimpleHTTPRequestHandler, Loggable):
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

	def title_identify(self, file_name, atype):
		movie = {}
		movie['file'] = file_name
		movie['type'] = atype
		self.log(str(movie))
		path = get_movie_path(movie)
		movie['stv_title_hash'] = stv_hash(path)
		movie['os_title_hash'] = hash_opensubtitle(path)
		
		# TODO: stv_subtitle_hash - hash of the subtitle file if present
		ident = {}
		translate_xbmc2stv_keys(ident, movie)

		# give api a hint about type if possible
		if movie['type'] in playable_types:
			ident['type'] = movie['type']

		# correct input
		if ident.get('imdb_id'):
			ident['imdb_id'] = ident['imdb_id'][2:]

		# try to get synopsi id
		self.log('to identify: ' + ident['file_name'])
		title = top.apiClient.titleIdentify(**ident)
		return title

	def path_search(self, url, qs):
		if not qs.get('q'):
			raise Exception('Missing parameter: q')

		file_name = qs['q'][0]

		self.send_response(200)
		self.send_header("Content-type", "text/xml")
		self.end_headers()


		title = self.title_identify(file_name, 'movie')		# TODO: put in the correct source type

		del(title['relevant_results'])

		# store 		
		self.server.cache[title['id']] = title

		xml_root = E.results(
			E.title(
				E.id( str(title['id']) )
			)
		)

		str_response = etree.tostring(xml_root, pretty_print=True)

		return str_response

	def path_get_detail(self, url, qs):
		stv_id = int(qs.get('q')[0])

		t = title = self.server.cache[stv_id]

		tpl = t.copy()

		# data transformations
		xml_directors = '\n'.join('<director>%s</director>' % director['name'] for director in t['directors'])
		xml_genres = '\n'.join('<genre>%s</genre>' % genre for genre in t['genres'])
		xml_cast = '\n'.join(['''
					<actor>
						<name>%s</name>
						<role>%s</role>
					</actor>''' % (actor['name'], actor['role']['name']) for actor in t['cast']])

		xml_thumbs = '<thumb>%(cover_large)s</thumb>' % tpl

		tpl['xml_directors'] = xml_directors
		tpl['xml_genres'] = xml_genres
		tpl['xml_cast'] = xml_cast
		tpl['xml_thumbs'] = xml_thumbs

		# self.log('--'*20)
		# self.log(dump(tpl))

		return '''
				<title>%(name)s</title>
				<year>%(year)s</year>
				%(xml_directors)s
				<top250></top250>
				<mpaa></mpaa>
				<tagline></tagline>
				<runtime>%(runtime)s</runtime>
				%(xml_thumbs)s
				<credits></credits>
				<rating></rating>
				<votes></votes>
				%(xml_genres)s
				%(xml_cast)s
				<outline></outline>
				<plot>%(plot)s</plot>
			''' % tpl


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
		self.serve_forever()

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
