import xbmc, xbmcgui, xbmcaddon
import os
import lib
from urllib2 import HTTPError, URLError
import json
import types

CANCEL_DIALOG  = ( 9, 10, 92, 216, 247, 257, 275, 61467, 61448, )
#CANCEL_DIALOG  = ( 9, 92, 216, 247, 257, 275, 61467, 61448, )

__addon__     = xbmcaddon.Addon()


def TrySendData(data, token):
    """
    Try to send data.
    """
    try:
        lib.send_data(data,token)
    except (URLError, HTTPError):
        tmpstring = __addon__.getSetting("SEND_QUEUE")
        try: 
            tmpData = json.loads(tmpstring)
        except ValueError:
            tmpData = []

        if type(tmpData) is not types.ListType:
            tmpData = []

        tmpData.append(data)
        tmpstring = json.dumps(tmpData)
        # tmpstring = tmpstring + json.dumps(self.data)

        __addon__.setSetting(id='SEND_QUEUE', value=tmpstring)



class XMLRatingDialog(xbmcgui.WindowXMLDialog):
    """docstring for XMLRatingDialog"""
    def __init__( self, *args, **kwargs ):
        self.data = {'type': "rating"}
        self.data['current time'] = kwargs['ctime']
        self.data['total time'] = kwargs['tottime']
        self.token = kwargs['token']
        self.data['Hashes'] = kwargs['hashd']
        #xbmc.log(str(args))
        #xbmc.log("SynopsiTV: Prepare to send. " + str(curtime) + " "+ str(totaltime))
    def message(self, message):
        dialog = xbmcgui.Dialog()
        dialog.ok(" My message title", message)
        self.close()
    def onInit( self ):
        pass
    def onClick( self, controlId ):
        if controlId == 11:
            xbmc.log("SynopsiTV: Rated Amazing")
            self.data['rating']  = "Amazing"
        elif controlId == 10:
            xbmc.log("SynopsiTV: Rated OK")
            self.data['rating']  = "OK"
        elif controlId == 15:
            xbmc.log("SynopsiTV: Rated Terrible")
            self.data['rating']  = "Terrible"
        else:
            xbmc.log("SynopsiTV: Not Rated")
            self.data['rating']  = "Not Rated"

        TrySendData(self.data, self.token)
        # try:
        #     lib.send_data(self.data,self.token)
        # except (URLError, HTTPError):
        #     tmpstring = __addon__.getSetting("SEND_QUEUE")
        #     tmpstring = tmpstring + json.dumps(self.data)
        #     __addon__.setSetting(id='SEND_QUEUE', value=tmpstring)
        # lib.send_data(self.data,self.token)


        self.close()
    def onFocus( self, controlId ):
        self.controlId = controlId

    def onAction( self, action ):
        if ( action.getId() in CANCEL_DIALOG):
            xbmc.log("SynopsiTV: Not Rated")
            self.data['rating']  = "Not Rated"
            #lib.send_data(self.data,self.token)
            # try:
            #     lib.send_data(self.data,self.token)
            # except (URLError, HTTPError):
            #     tmpstring = __addon__.getSetting("SEND_QUEUE")
            #     tmpstring = tmpstring + json.dumps(self.data)
            #     __addon__.setSetting(id='SEND_QUEUE', value=tmpstring)
            TrySendData(self.data,self.token)
            self.close()

        
