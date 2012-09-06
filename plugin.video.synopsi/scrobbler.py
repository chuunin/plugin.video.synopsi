import xbmc, xbmcgui, xbmcaddon
import threading
import time

import library


CANCEL_DIALOG = (9, 10, 92, 216, 247, 257, 275, 61467, 61448, )
# Default XBMC constant for hidden cancel button

__addon__     = xbmcaddon.Addon()
__addonname__ = __addon__.getAddonInfo('name')
__cwd__       = __addon__.getAddonInfo('path')
__author__    = __addon__.getAddonInfo('author')
__version__   = __addon__.getAddonInfo('version')
__language__  = __addon__.getLocalizedString

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
    ended_without_rating = False

    playing = False
    media_file = None

    def __init__(self):
        xbmc.Player.__init__(self)

    def onPlayBackStarted(self):
        if self.playing:
            if self.media_file != xbmc.Player().getPlayingFile():
                self.ended_without_rating = True
                self.started = True
                self.playing = True
                self.media_file = xbmc.Player().getPlayingFile()
        else:
            if xbmc.Player().isPlayingVideo():
                self.started = True
                self.playing = True
                self.media_file = xbmc.Player().getPlayingFile()

    def onPlayBackEnded(self):
        if self.playing:
            try:
                self.media_file = xbmc.Player().getPlayingFile()
            except Exception, e:
                # TODO: Handle if API will change
                if "XBMC is not playing any file" in e:
                    self.ended = True
                    self.playing = False
                    self.media_file = None

    def onPlayBackStopped(self):
        if self.playing:
            self.stopped = True
            self.playing = False
            self.media_file = None

    def onPlayBackPaused(self):
        if self.playing:
            self.paused = True

    def onPlayBackResumed(self):
        if self.playing:
            self.resumed = True


class XMLRatingDialog(xbmcgui.WindowXMLDialog):
    """
    Dialog class that asks user about rating of movie.
    """
    response = 4
    # 1 = Amazing, 2 = OK, 3 = Terrible, 4 = Not rated
    def __init__(self, *args, **kwargs):
        xbmcgui.WindowXMLDialog.__init__( self )
 
    def onInit(self):
        self.getString = __addon__.getLocalizedString
        self.getControl(11).setLabel(self.getString(69601))
        self.getControl(10).setLabel(self.getString(69602))
        self.getControl(15).setLabel(self.getString(69603))
        self.getControl(1 ).setLabel(self.getString(69604))
        self.getControl(2 ).setLabel(self.getString(69600))

    def onClick(self, controlId):
        """
        For controlID see: <control id="11" type="button"> in SynopsiDialog.xml
        """
        if controlId == 11:
            self.response = 1
        elif controlId == 10:
            self.response = 2
        elif controlId == 15:
            self.response = 3
        else:
            self.response = 4
        self.close()

    def onAction(self, action):
        if (action.getId() in CANCEL_DIALOG):
            self.response = 4
            self.close()


def get_rating():
    """
    Get rating from user:
    1 = Amazing, 2 = OK, 3 = Terrible, 4 = Not rated
    """
    ui = XMLRatingDialog("SynopsiDialog.xml", __cwd__, "Default")
    ui.doModal()
    _response = ui.response
    del ui
    return _response


def is_in_library():
    return True


class Scrobbler(threading.Thread):
    """
    Just a Scrobbler.
    """
    def __init__(self):
        super(Scrobbler, self).__init__()
        import json
        print xbmc.executeJSONRPC(json.dumps(
            {'params':
                {
                    # 'properties': properties
                },
                'jsonrpc': '2.0',
                'method': "JSONRPC.Introspect",
                'id': 1
                }   ))

    def started(self):
        notification("started", "started")

    def ended(self):
        notification("ended", "ended")
        if is_in_library():
            get_rating()

    def ended_without_rating(self):
        notification("ended", "ended")

    def stopped(self):
        notification("stopped", "stopped")
        if self.current_time > 0.7 * self.total_time:
            # ask for rating only if stopped and more than 70% of movie passed
            if is_in_library():
                get_rating()

    def paused(self):
        notification("paused", "paused")

    def resumed(self):
        notification("resumed", "resumed")

    def run(self):
        self.player = SynopsiPlayer()

        while (not library.ABORT_REQUESTED): # while (not xbmc.abortRequested):
            xbmc.sleep(200)# wait 200 ms

            if self.player.ended_without_rating:
                self.ended_without_rating()
                self.player.ended_without_rating = False

            if self.player.started:
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

            if self.player.playing:
                try:
                    self.current_time = xbmc.Player().getTime()
                except Exception, e:
                    # TODO: Handle if API will change
                    if not "XBMC is not playing any media file" in e:
                        raise e
