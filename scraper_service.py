

# python standart lib
import sys, json, urlparse
import BaseHTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler


class ScraperServer(BaseHTTPServer.HTTPServer):
	def __init__(self, server_address):
		BaseHTTPServer.HTTPServer.__init__(self, server_address, ScraperRequestHandler)

class ScraperRequestHandler(SimpleHTTPRequestHandler):
	protocol_version = "HTTP/1.0"


	def do_GET(s):
		url = urlparse.urlparse(s.path)
		qs = urlparse.parse_qs(url.query)
		print qs
		
		s.send_response(200)
		s.send_header("Content-type", "text/json")
		s.end_headers()

		response = {}
		response['container'] = 'garbage'

		s.wfile.write(json.dumps(response))

if __name__ == '__main__':
	server_address = ('127.0.0.1', 9099)
	httpd = ScraperServer(server_address)
	sa = httpd.socket.getsockname()
	print "Serving HTTP on", sa[0], "port", sa[1], "..."

	try:
		httpd.serve_forever()
	except KeyboardInterrupt:
		pass
	httpd.server_close()
