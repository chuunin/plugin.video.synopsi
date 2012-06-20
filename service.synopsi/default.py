import xbmc
import xbmcgui
import xbmcaddon
import json
import urllib2
from urllib2 import HTTPError
import re
import uuid
#Local imports
import RatingDialog
import lib


def Notification(Name, Text):
    """Sends notification to XBMC."""
    xbmc.executebuiltin('XBMC.Notification(' + str(Name) +',' + str(Text) +',1)')

def Login(username, password):
    """Login function."""
    global loginFailed
    try:
        pass
        token = lib.get_token(username, password)
        __addon__.setSetting(id='ACCTOKEN', value=token[0])
        __addon__.setSetting(id='REFTOKEN', value=token[1])
        __addon__.setSetting(id='BOOLTOK', value="true")
        #Deleting Password
        pss  = '*'*len(password)
        __addon__.setSetting(id='PASS', value=pss)
    except HTTPError, e:
        if e.code == 400:
            if not loginFailed:
                Notification("SynopsiTV","Login failed")
            loginFailed = True

def GenerateOSInfo():
    """Function that generates unique device info."""
    uid = str(uuid.uuid4())
    #TODO: Add OS specific info.


def SendInfoStart(plyer, status):
    """Function that sends json of current video status."""
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
    lib.send_data(data,__addon__.getSetting("ACCTOKEN"))

    """
    req=urllib2.Request('http://dev.synopsi.tv/api/desktop/', data=json.dumps({'data':data, 'token': 12345}),
                        headers={'content-type':'application/json', 'user-agent': 'linux'},
                        origin_req_host='dev.synopsi.tv')
    f = urllib2.urlopen(req)
    
    xbmc.log('SynopsiTV: Response: ' + f.read())
    """

def runQuery():
    #xbmc.log(str(xbmc.executehttpapi("queryvideodatabase(SELECT path.strPath, files.strFilename FROM path,files WHERE path.idPath=files.idPath)")))

    """
    NIGHTMAREEEE
    xbmc.log(str(xbmc.executehttpapi("queryvideodatabase(SELECT path.strPath, strFilename FROM path, files WHERE path.idPath=idPath)")))
    xbmc.log(str(xbmc.executehttpapi("queryvideodatabase(SELECT strPath FROM path, files)")))
    xbmc.log(str(xbmc.executehttpapi("queryvideodatabase(SELECT path.strPath FROM path, files)")))
    xbmc.log(str(xbmc.executehttpapi("queryvideodatabase(SELECT files.strFilename FROM files, path)")))
    xbmc.log(str(xbmc.executehttpapi("queryvideodatabase(SELECT strFilename FROM files)")))
    xbmc.log(str(xbmc.executehttpapi("queryvideodatabase(SELECT%20path.strPath,%20files.strFilename%20FROM%20path,files%20WHERE%20path.idPath=files.idPath)")))
    """
    #xbmc.log(str(xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": {"properties": ["file", "fanart", "thumbnail"]}, "id": 1}')))
    xbmc.log(str(xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": {"properties": ["file","imdbnumber"]}, "id": 1}')))
def queryVideoDB(sql, numofcol=1):
    def chunks(l, n):
            return [l[i:i+n] for i in range(0, len(l), n)]
    if numofcol == 1:
        xml = xbmc.executehttpapi("queryvideodatabase({0})".format(sql))
        fields = re.compile("<field>(.+?)</field>").findall(xml.replace("\n",""))
        return fields
    else:
        xml = xbmc.executehttpapi("queryvideodatabase({0})".format(sql))
        fields = re.compile("<field>(.+?)</field>").findall(xml.replace("\n",""))
        return chunks(fields, numofcol)

def sendXBMCQuery(query):
    req = urllib2.Request(url=str('http://localhost/xbmcCmds/xbmcHttp?command=queryvideodatabase({0})'.format(lib.url_fix(query))))
    f = urllib2.urlopen(req)
    return f.read()

def LogQuery(query):
    xbmc.log("----------------------------------------------------------------------------------------------------------------")
    xbmc.log(query)
    xbmc.log(sendXBMCQuery(query))

def runLibSearchOld():
    """Function that runs on first start."""
    def chunks(l, n):
            return [l[i:i+n] for i in range(0, len(l), n)]
    
    req = urllib2.Request(url='http://localhost/xbmcCmds/xbmcHttp?command=queryvideodatabase(select%20all%20c16,%20c00,%20c09,%20c22%20from%20movie)')
    f = urllib2.urlopen(req)

    fread = f.read()
    #xbmc.log('XML: ' + fread)
    fields = re.compile("<field>(.+?)</field>").findall(fread.replace("\n",""))
    #TODO: Add full data send

    #http://localhost/xbmcCmds/xbmcHttp?command=queryvideodatabase(select%20count%20(idMovie)%20from%20movie)
    #SELECT COUNT(idMovie) FROM movie


    """
    header = ["Primary Key", "Local Movie Title", "Movie Plot", "Movie Plot Outline", "Movie Tagline",
              "Rating Votes", "Rating", "Writers", "Year Released", "Thumbnails", "IMDB ID", "Title formatted for sorting",
              "Runtime", "MPAA Rating", "listed as Top250", "Genre", "Director", "Original Movie Title", "listed as Thumbnail URL Spoof",
              "Studio", "Trailer URL", "Fanart URLs", "Country", "Path", "idPath"]
    """

    head = ["Original Movie Title", "Local Movie Title", "IMDB ID", "Path"]

    result= []
    #xbmc.log(str(fields))
    for movie in chunks(fields, 4):
            result.append(dict(zip(head, movie)))
            

    xbmc.log(json.dumps({'data':result, 'token' : 12345}))


    #xbmc.log(sendXBMCQuery("SELECT COUNT(idFile) FROM files"))

    #LogQuery("SELECT COUNT(idFile) FROM files")

    fread =LogQuery("SELECT COUNT(idFile) FROM files")
    fields = re.compile("<field>(.+?)</field>").findall(fread.replace("\n",""))
    numfiles = int(__addon__.getSetting("numfiles"))

    #if int(fields[0]) > numfiles:



    #TODO: Sending data

    """
idMovie	 integer	 Primary Key
c00	 text	 Local Movie Title
c01	 text	 Movie Plot
c02	 text	 Movie Plot Outline
c03	 text	 Movie Tagline
c04	 text	 Rating Votes
c05	 text	 Rating
c06	 text	 Writers
c07	 text	 Year Released
c08	 text	 Thumbnails
c09	 text	 IMDB ID
c10	 text	 Title formatted for sorting
c11	 text	 Runtime [UPnP devices see this as seconds]
c12	 text	 MPAA Rating
c13	 text	 [unknown - listed as Top250]
c14	 text	 Genre
c15	 text	 Director
c16	 text	 Original Movie Title
c17	 text	 [unknown - listed as Thumbnail URL Spoof]
c18	 text	 Studio
c19	 text	 Trailer URL
c20	 text	 Fanart URLs
c21	 text	 Country (Added in r29886[1]
c23	 text	 idPath
    """

def runLibSearch():
    """Find users movies."""
    xbmc.log("SynopsiTV: Querying")
    #xbmc.log(str(queryVideoDB("SELECT ALL strFilename from files",1)))

    xbmc.log(str(queryVideoDB("SELECT COUNT(idMovie) FROM movie",1)))
    xbmc.log(str(queryVideoDB("SELECT idMovie,c00 FROM movie",1)))
    #for mfile in queryVideoDB("SELECT ALL idFile, idPath, strFilename, playCount, lastPlayed from files",5):
    #    if not "stack://" in mfile[2]:
    #for mfile in queryVideoDB("SELECT All path.strPath, files.strFilename FROM path INNER JOIN files ON path.idPath=files.idPath", 2):
    """
    for mfile in queryVideoDB("SELECT path.strPath, files.strFilename FROM path,files WHERE path.idPath=files.idPath", 2):
        if not "stack://" in mfile[1]:
            xbmc.log(str(mfile[0]+mfile[1]))
    """
        
        
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
#Notification("SynopsiTV: STARTUP")


if __addon__.getSetting("BOOLTOK") == "false":
    Notification("SynopsiTV","Opening Settings")
    __addon__.openSettings()



xbmc.log('SynopsiTV: NEW CLASS PLAYER')
class SynopsiPlayer(xbmc.Player) :
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
            ui = RatingDialog.XMLRatingDialog("SynopsiDialog.xml" , __cwd__, "Default", ctime=curtime, tottime=totaltime, token=__addon__.getSetting("ACCTOKEN"))
            ui.doModal()
            del ui
            
    def onPlayBackStopped(self):
        if (VIDEO == 1):
            xbmc.log('SynopsiTV: PLAYBACK STOPPED')

            #ask about experience when > 70% of film

            if curtime > totaltime * 0.7:
                ui = RatingDialog.XMLRatingDialog("SynopsiDialog.xml" , __cwd__, "Default", ctime=curtime, tottime=totaltime, token=__addon__.getSetting("ACCTOKEN"))
                ui.doModal()
                del ui
            else:
                pass                    

            ######
            #ui = RatingDialog.XMLRatingDialog("SynopsiDialog.xml" , __cwd__, "Default", ctime=curtime, tottime=totaltime)
            #ui.doModal()
            #del ui
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
            

player=SynopsiPlayer()
#xbmc.log('SynopsiTV: ------------------->TEST')

runQuery()
runLibSearch()

loginFailed = False

curtime, totaltime = (0,0)

while (not xbmc.abortRequested):
    if xbmc.Player().isPlayingVideo():
        VIDEO = 1
        curtime = xbmc.Player().getTime()
        totaltime = xbmc.Player().getTotalTime()
    else:
        VIDEO = 0

    xbmc.sleep(500)
    if (__addon__.getSetting("BOOLTOK") == "false") and (__addon__.getSetting("USER") != "") and (__addon__.getSetting("PASS") != ""):
        if not loginFailed:
            xbmc.log("SynopsiTV: Trying to login")
            Login(__addon__.getSetting("USER"),__addon__.getSetting("PASS"))

    #xbmc.log('VIDEO=' + str(VIDEO))

while (xbmc.abortRequested):
    xbmc.log('SynopsiTV: Aborting...')

