# import xbmc, xbmcgui, xbmcaddon
import threading
import time


class Scrobbler(threading.Thread):
	"""
	Just a Scrobbler.
	"""
	def __init__(self):
		super(Scrobbler, self).__init__()

	def run(self):
		while True:
			time.sleep(1)	