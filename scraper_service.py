

# python standart lib
import sys
import json
import urlparse
import traceback
from lxml.builder import E
from lxml import etree
import BaseHTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
from threading import Thread
from httplib2 import Http
from app_apiclient import AppApiClient


class ScraperServer(BaseHTTPServer.HTTPServer):
	def __init__(self, server_address):
		BaseHTTPServer.HTTPServer.__init__(self, server_address, ScraperRequestHandler)

class ScraperRequestHandler(SimpleHTTPRequestHandler):
	protocol_version = "HTTP/1.0"


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

		print self.path
		print str_response

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
		title = {
			'id': '22',
			'name': file_name,
			'runtime': '121',
			'genres': ['Sci-fi', 'Drama'],
			'cast': ['Elon Musk', 'Keanu Reeves']
		}

		# create xml from title
		genres  = E.genres()
		cast = E.cast()		
		for genre in title['genres']:
			e = etree.SubElement(genres, 'genre')
			e.text = genre

		for actor_name in title['cast']:
			e = etree.SubElement(cast, 'actor')
			e.text = actor_name

		xml_root = E.results(
			E.title(
				E.id( title['id'] ),
				E.name( title['name'] ),
				E.runtime( title['runtime'] ),
				genres,
				cast
			)
		)

		str_response = etree.tostring(xml_root, pretty_print=True)

		return str_response

	def path_get_detail(self, url, qs):
		name = qs.get('q')[0]

		# return '<xxx>get_detail_result</xxx>'
		return '''
			<details>
				<title>%s</title>
				<year></year>
				<director></director>
				<top250></top250>
				<mpaa></mpaa>
				<tagline></tagline>
				<runtime></runtime>
				<thumb></thumb>
				<credits></credits>
				<rating></rating>
				<votes></votes>
				<genre></genre>
				<actor>
					<name></name>
					<role></role>
				</actor>
				<outline></outline>
				<plot></plot>
			</details>''' % name


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

	top.apiClient = AppApiClient.getDefaultClient()

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
