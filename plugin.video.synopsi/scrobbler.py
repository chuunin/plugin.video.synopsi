import xbmc, xbmcgui, xbmcaddon
import threading
import time

import library


CANCEL_DIALOG = (9, 10, 92, 216, 247, 257, 275, 61467, 61448, )

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

    playing = False

    def __init__(self):
        xbmc.Player.__init__(self)

    def onPlayBackStarted(self):
        if xbmc.Player().isPlayingVideo():
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
        if controlId == 11:
            # xbmc.log("SynopsiTV: Rated Amazing")
            self.response = 1
        elif controlId == 10:
            # xbmc.log("SynopsiTV: Rated OK")
            self.response = 2
        elif controlId == 15:
            # xbmc.log("SynopsiTV: Rated Terrible")
            self.response = 3
        else:
            # xbmc.log("SynopsiTV: Not Rated")
            self.response = 4
        self.close()

    def onAction(self, action):
        if (action.getId() in CANCEL_DIALOG):
            # xbmc.log("SynopsiTV: Not Rated")
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


class Scrobbler(threading.Thread):
    """
    Just a Scrobbler.
    """
    def __init__(self):
        super(Scrobbler, self).__init__()

    def started(self):
        notification("started", "started")

    def ended(self):
        notification("ended", "ended")
        get_rating()

    def stopped(self):
        notification("stopped", "stopped")
        if self.current_time > 0.7 * self.total_time:
            get_rating()

    def paused(self):
        notification("paused", "paused")

    def resumed(self):
        notification("resumed", "resumed")

    def run(self):
        self.player = SynopsiPlayer()

        while (not library.ABORT_REQUESTED): # while (not xbmc.abortRequested):
            xbmc.sleep(200)

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
                    if not "XBMC is not playing any media file" in e:
                        raise e
