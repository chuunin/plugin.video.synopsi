import xbmc, xbmcgui, xbmcplugin, xbmcaddon
import sys

CANCEL_DIALOG = (7, 9, 10, 92, 216, 247, 257, 275, 61467, 61448, )
class XMLRatingDialog(xbmcgui.WindowXML):
# class XMLRatingDialog(xbmcgui.WindowXMLDialog):
    """
    Dialog class that asks user about rating of movie.
    """
    def __init__(self, *args, **kwargs):
        # self.data = {'event': "Dialog.Rating"}
        # self.data['currenttime'] = kwargs['ctime']
        # self.data['totaltime'] = kwargs['tottime']
        # self.token = kwargs['token']
        # self.data['hashes'] = kwargs['hashd']
        #xbmc.log(str(args))
        pass

    def message(self, message):
        """
        Shows xbmc dialog with OK and message.
        """
        dialog = xbmcgui.Dialog()
        dialog.ok(" My message title", message)
        self.close()

    def onInit(self):
        pass

    def onClick(self, controlId):
        pass
        xbmc.log(str(controlId))
        # if controlId == 11:
        #     xbmc.log("SynopsiTV: Rated Amazing")
        #     self.data['rating'] = "Amazing"
        # elif controlId == 10:
        #     xbmc.log("SynopsiTV: Rated OK")
        #     self.data['rating'] = "OK"
        # elif controlId == 15:
        #     xbmc.log("SynopsiTV: Rated Terrible")
        #     self.data['rating'] = "Terrible"
        # else:
        #     xbmc.log("SynopsiTV: Not Rated")
        #     self.data['rating'] = "Not Rated"

        # global queue
        # queue.add_to_queue(self.data)
        # self.close()

    def onFocus(self, controlId):
        self.controlId = controlId

    def onAction(self, action):
        if (action.getId() in CANCEL_DIALOG):
            # sys.exit()
            # xbmc.executebuiltin("ReplaceWindow(10000)")
            xbmc.executebuiltin("ActivateWindow(Home)")
            self.close()