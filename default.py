import xbmc
import xbmcgui
import xbmcaddon
import json
import urllib2
import sqlite3

def SendInfoStart(plyer, status):
        InfoTag = plyer.getVideoInfoTag()
        data = {'File': InfoTag.getFile(),
                'File2': plyer.getPlayingFile(),
                'Time': plyer.getTime(),
                'TotalTime': plyer.getTotalTime(),
                #'SeekTime': plyer.seekTime(),
                'Path': InfoTag.getPath(),
                'Title': InfoTag.getTitle(),
                'IMDB': InfoTag.getIMDBNumber(),
                'Status': status}
        #xbmc.log(json.dumps(data))


        req=urllib2.Request('http://dev.synopsi.tv/api/desktop/', data=json.dumps({'data':data, 'token': 12345}),
                            headers={'content-type':'application/json', 'user-agent': 'linux'},
                            origin_req_host='dev.synopsi.tv')
        f = urllib2.urlopen(req)
        
        xbmc.log('SynopsiTV: Response: ' + f.read())



def runLibSearch():
        req = urllib2.Request(url='http://localhost/xbmcCmds/xbmcHttp?command=queryvideodatabase(select%20all%20c00%20from%20movie)')
        f = urllib2.urlopen(req)
        xbmc.log('SynopsiTV: Response: ' + f.read())
        
        


# ADDON INFORMATION
__addon__     = xbmcaddon.Addon()
__addonname__ = __addon__.getAddonInfo('name')
__cwd__       = __addon__.getAddonInfo('path')
__author__    = __addon__.getAddonInfo('author')
__version__   = __addon__.getAddonInfo('version')
xbmc.log('SynopsiTV: Addon information')
xbmc.log('SynopsiTV: ----> Addon name    : ' + __addonname__)
xbmc.log('SynopsiTV: ----> Addon path    : ' + __cwd__)
xbmc.log('SynopsiTV: ----> Addon author  : ' + __author__ )
xbmc.log('SynopsiTV: ----> Addon version : ' + __version__)

xbmc.log('SynopsiTV: STARTUP')

xbmc.log('SynopsiTV: NEW CLASS PLAYER')
class MyPlayer(xbmc.Player) :
    xbmc.log('SynopsiTV: Class player is opened')
    
    def __init__ (self):
        xbmc.Player.__init__(self)
        xbmc.log('SynopsiTV: Class player is initialized')
        
    def onPlayBackStarted(self):
        if xbmc.Player().isPlayingVideo():
            xbmc.log('SynopsiTV: PLAYBACK STARTED')
            SendInfoStart(xbmc.Player(),'started')
            
    def onPlayBackEnded(self):
        if (VIDEO == 1):
            xbmc.log('SynopsiTV: PLAYBACK ENDED')
            #SendInfoStart(xbmc.Player(),'ended')
            #TODO: dorobit end
            
    def onPlayBackStopped(self):
        if (VIDEO == 1):
            xbmc.log('SynopsiTV: PLAYBACK STOPPED')
            #SendInfoStart(xbmc.Player(),'stopped')
            #TODO: dorobit stop
            
    def onPlayBackPaused(self):
        if xbmc.Player().isPlayingVideo():
            xbmc.log('SynopsiTV: PLAYBACK PAUSED')
            SendInfoStart(xbmc.Player(),'paused')
            
    def onPlayBackResumed(self):
        if xbmc.Player().isPlayingVideo():
            xbmc.log('SynopsiTV: PLAYBACK RESUMED')
            SendInfoStart(xbmc.Player(),'resumed')
            
player=MyPlayer()
xbmc.log('SynopsiTV: ------------------->TEST')

runLibSearch()

while (not xbmc.abortRequested):
    if xbmc.Player().isPlayingVideo():
        VIDEO = 1
    else:
        VIDEO = 0

    xbmc.sleep(500)
    #xbmc.log('VIDEO=' + str(VIDEO))

while (xbmc.abortRequested):
    xbmc.log('SynopsiTV: Aborting...')

