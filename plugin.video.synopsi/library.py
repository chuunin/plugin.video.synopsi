# import xbmc, xbmcgui, xbmcaddon
import threading
import time

class Library(threading.Thread):
	"""
	Just a Library.
	"""
	def __init__(self):
		super(Library, self).__init__()

	def run(self):
		while True:
			time.sleep(1)
