import xbmc, xbmcgui, xbmcaddon
import threading
import time


def notification(name, text):
    """
    Sends notification to XBMC.
    """
    xbmc.executebuiltin("XBMC.Notification({0},{1},1)".format(name, text))

class SynopsiPlayer(xbmc.Player):
    started = False
    ended = False
    stopped = False
    paused = False
    resumed = False

    playing = False

    def __init__(self):
        xbmc.Player.__init__(self)

    def onPlayBackStarted(self):
    	if xbmc.isPlayingVideo():
    		self.started = True
    		self.playing = True

    def onPlayBackEnded(self):
    	if self.playing:
    		self.ended = True
    		self.playing = False

    def onPlayBackStopped(self):
    	if self.playing:
    		self.stopped = True
    		self.playing = False

    def onPlayBackPaused(self):
    	if self.playing:
    		self.paused = True

    def onPlayBackResumed(self):
    	if self.playing:
    		self.resumed = True


class Scrobbler(threading.Thread):
	"""
	Just a Scrobbler.
	"""
	def __init__(self):
		super(Scrobbler, self).__init__()

	def started(self):
		pass

	def ended(self):
		pass

	def stopped(self):
		pass

	def paused(self):
		pass

	def resumed(self):
		pass


	def run(self):
		self.player = SynopsiPlayer()
		while (not xbmc.abortRequested):
			xbmc.sleep(100)
			
			if self.player.playing:
				self.current_time = xbmc.Player().getTime()
			
			if self.player.started:
				notification("started", "started")
				self.total_time = xbmc.Player().getTotalTime()
				self.started()
				self.player.started = False

			if self.player.ended:
				self.ended()
				self.player.ended = False

			if self.player.stopped:
				self.stopped()
				self.player.stopped = False

			if self.player.paused:
				self.paused()
				self.player.paused = False

			if self.player.resumed:
				self.resumed()
				self.player.resumed = False

