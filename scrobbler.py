import xbmc, xbmcgui, xbmcaddon
# except ImportError:
#     from tests import xbmc, xbmcgui, xbmcaddon
import threading
import time
from random import randint
import library
import xbmcplugin
from app_apiclient import AppApiClient
import logging
import json
from utilities import *

CANCEL_DIALOG = (9, 10, 92, 216, 247, 257, 275, 61467, 61448, )
# Default XBMC constant for hidden cancel button

__addon__  = get_current_addon()
__addonname__ = __addon__.getAddonInfo('name')
__cwd__       = __addon__.getAddonInfo('path')
__author__    = __addon__.getAddonInfo('author')
__version__   = __addon__.getAddonInfo('version')
__language__  = __addon__.getLocalizedString

class SynopsiPlayer(xbmc.Player):
    """ Bugfix and processing layer """
    started = False
    ended = False
    stopped = False
    paused = False
    ended_without_rating = False
    apiclient = None

    playing = False
    media_file = None
    last_played_file = None
    playerEvents = []

    def __init__(self):
        super(SynopsiPlayer, self).__init__()
        self.log('INIT')
        self.current_time = 0

        self.apiclient = AppApiClient.getDefaultClient()

    def log(self, msg):
        xbmc.log('SynopsiPlayer: ' + msg)

    def playerEvent(self, eventName):
        notification(eventName, 'notify')
        self.log(eventName)

        event = {
            'event': eventName,                
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }

        if self.playing:
            event['movieTime'] = self.current_time

        self.playerEvents.append(event)

    def onPlayBackStarted(self):
        self.log('onPlayBackStarted')
        # this is just next file of a movie
        if self.playing:
            if self.media_file != xbmc.Player().getPlayingFile():
                self.ended_without_rating()
                self.media_file = xbmc.Player().getPlayingFile()
                self.last_played_file = self.media_file
                self.subtitle_file = self.getSubtitles()
        
        # started new video playback
        else:
            if xbmc.Player().isPlayingVideo():
                self.playing = True
                self.total_time = xbmc.Player().getTotalTime()
                self.current_time = self.get_time_or_none()
                self.started()
                self.media_file = xbmc.Player().getPlayingFile()
                self.last_played_file = self.media_file
                self.subtitle_file = self.getSubtitles()
                self.log('subtitle_file:' + str(self.subtitle_file))

        self.log('playing:' + str(self.playing))

    def onPlayBackEnded(self):
        notification("onPlayBackEnded", "onPlayBackEnded")
        if self.playing:
            try:
                self.media_file = xbmc.Player().getPlayingFile()
            except Exception, e:
                # TODO: Handle if API will change
                if "XBMC is not playing any file" in e:
                    self.playing = False
                    self.media_file = None
                    self.ended()

    def onPlayBackStopped(self):
        self.log('onPlayBackStopped')
        if self.playing:
            self.stopped()
            self.playing = False
            self.media_file = None

    def onPlayBackPaused(self):
        self.log('onPlayBackPaused')
        if self.playing:
            self.paused()

    def onPlayBackResumed(self):
        if self.playing:
            self.resumed()
        else:
            self.log('resumed not playing?')
    
    def get_time_or_none(self):
        try:
            t = 0
            t = self.getTime()
        except:
            return None

        return t


class SynopsiPlayerDecor(SynopsiPlayer):
    """ This class defines methods that are called from the bugfix and processing parent class"""
    def __init__(self):
        super(SynopsiPlayerDecor, self).__init__()

    def setStvList(self, cache):
        self.cache = cache

    def started(self):
        self.playerEvent('start')

    def ended(self):
        self.playerEvent('end')
        if self.cache.hasFilename(self.last_played_file):
            get_rating()
            

    def ended_without_rating(self):
        self.playerEvent('end')

    def stopped(self):  
        self.playerEvent('stop')
        self.log(json.dumps(self.playerEvents, indent=4))
        self.log('time:' + str(self.current_time))

        # ask for 'rating only if stopped and more than 70% of movie passed
        if self.cache.hasFilename(self.last_played_file):
            rating = get_rating()

            # if user rated the title
            if rating < 4:
                # temporary:
                # get the title id
                # query cache to get stvId
                detail = self.cache.getByFilename(self.last_played_file)

                # get stv id
                self.log('detail: ' + str(detail))
                if detail.has_key('stvId'):
                    data = { 'rating': rating, 'player_events': self.playerEvents }
                    self.apiclient.titleWatched(detail['stvId'], **data)
                self.playerEvents = []


    def paused(self):
        self.playerEvent('pause')

    def resumed(self):
        self.playerEvent('resume')

class Scrobbler(threading.Thread):
    """
    Thread creates SynopsiPlayer to receive events and waits for ABORT request.
    """
    def __init__(self, xcache):
        super(Scrobbler, self).__init__()
        self.log('Created Scrobbler thread')
        self.cache = xcache

    def log(self, msg):
        xbmc.log('Scrobbler: ' + msg)

    def run(self):
        self.log('thread run start')

        player = SynopsiPlayerDecor()
        player.setStvList(self.cache)

        #   wait for abort flag
        while not library.ABORT_REQUESTED and not xbmc.abortRequested:
            player.current_time = player.get_time_or_none()
            # self.log('time:' + str(player.current_time))

            xbmc.sleep(500)
        
        dbg = ''
        if library.ABORT_REQUESTED: dbg += "library.ABORT_REQUESTED " 
        if xbmc.abortRequested: dbg += "xbmc.abortRequested " 
        
        self.log("thread run end " + dbg)

