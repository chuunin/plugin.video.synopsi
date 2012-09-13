try:
    import xbmc, xbmcgui, xbmcaddon
except ImportError:
    from tests import xbmc, xbmcgui, xbmcaddon
import threading
import time
from random import randint
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
    xbmc.log('Notification:' + name + ' ' + text)

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


class SynopsiPlayer(xbmc.Player):
    """ Bugfix and processing layer """
    started = False
    ended = False
    stopped = False
    paused = False
    ended_without_rating = False

    playing = False
    media_file = None

    def __init__(self):
        super(SynopsiPlayer, self).__init__()
        self.log('INIT')
        self.current_time = 0

    def log(self, msg):
        xbmc.log('SynopsiPlayer: ' + msg)

    def onPlayBackStarted(self):
        self.log('onPlayBackStarted')
        if self.playing:
            if self.media_file != xbmc.Player().getPlayingFile():
                self.ended_without_rating()
                self.playing = True
                self.media_file = xbmc.Player().getPlayingFile()
        else:
            if xbmc.Player().isPlayingVideo():
                self.started()
                self.playing = True
                self.media_file = xbmc.Player().getPlayingFile()

    def onPlayBackEnded(self):
        notification("onPlayBackEnded", "Dev Notice")
        self.log('onPlayBackEnded')
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
            self.playing = False
            self.media_file = None
            self.stopped()


    def onPlayBackPaused(self):
        self.log('onPlayBackPaused')
        if self.playing:
            self.paused()

    def onPlayBackResumed(self):
        if self.playing:
            self.resumed()
    

class SynopsiPlayerDecor(SynopsiPlayer):
    """ This class defines methods that are called from the bugfix and processing parent class"""
    def __init__(self):
        super(SynopsiPlayerDecor, self).__init__()

    def __del__(self):
        self.log('Deleting Player Object')

    def started(self):
        self.total_time = xbmc.Player().getTotalTime()
        notification("started", "started")

    def ended(self):
        self.log('ended')
        notification("ended", "ended")
        if is_in_library():
            get_rating()

    def ended_without_rating(self):
        notification("ended", "ended")

    def stopped(self):  
            # ask for rating only if stopped and more than 70% of movie passed
            if is_in_library():
                get_rating()

    def paused(self):
        notification("paused", "paused")

    def resumed(self):
        notification("resumed", "resumed")

class Scrobbler(threading.Thread):
    """
    Layer that defines final methods.
    """
    def __init__(self):
        super(Scrobbler, self).__init__()
        self.log('Created Scrobbler thread')

    def log(self, msg):
        xbmc.log('Scrobbler: ' + msg)

    def run(self):
        self.log('thread run start')
        p = SynopsiPlayerDecor()
        #   wait for abort flag
        while not library.ABORT_REQUESTED:
            xbmc.sleep(2000)
            self.log('..scrobb..' + str(randint(0, 100)))
        
        self.log("thread run end")

        """
            if self.player.playing:
                try:
                    self.current_time = xbmc.Player().getTime()
                except Exception, e:
                    # TODO: Handle if API will change
                    if not "XBMC is not playing any media file" in e:
                        raise e

            self.log("Scrobbler thread end")
        """         
           
 