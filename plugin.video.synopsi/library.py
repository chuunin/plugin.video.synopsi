import xbmc, xbmcgui, xbmcaddon
import threading
import time
import socket
import json

ABORT_REQUESTED = False

class ApiThread(threading.Thread):
    def __init__(self):
        super(ApiThread, self).__init__()
        self.sock = socket.socket()
        self.sock.settimeout(None)
        self.sock.connect(("localhost", 9090))
        # self.sock.connect(("localhost", get_api_port()))

    def run(self):
    	global ABORT_REQUESTED    
        while True:
            data = self.sock.recv(1024)
            xbmc.log('At {0}: {1}'.format(time.time(), str(data)))
            try:
                data_json = json.loads(str(data))
                method = data_json.get("method")

                API_CACHE = data_json.copy()
            except ValueError:
                continue

            if method == "System.OnQuit":
                ABORT_REQUESTED = True
                break
            else:
                # self.process(data_json)
                pass


class Library(threading.Thread):
	"""
	Just a Library.
	"""
	def __init__(self):
		super(Library, self).__init__()

	def create(self):
		pass

	def read(self):
		pass

	def update(self):
		pass

	def delete(self):
		pass

	def run(self):
		global ABORT_REQUESTED

		ApiThread().start()
		while (not ABORT_REQUESTED): # while (not xbmc.abortRequested): # XBMC bug
			xbmc.sleep(1000)
