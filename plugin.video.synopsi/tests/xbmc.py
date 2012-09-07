import logging
import sys
import SocketServer
import socket
import threading
import time
import json


abortRequested = False

def sleep(tim):
    pass


def log(string):
    print string


def executeJSONRPC(js):
    print "XBMC recieved: ", js.strip()
    return "{}"


def executebuiltin(builtin):
    if "XBMC.Notification" in builtin:
        pass
        a = builtin.split(",")
        print "XBMC message:", a[0].strip("XBMC.Notification("), a[1]
    else:
        print "Executed Builtin:", builtin


class Player(object):
    def __init__(self):
        super(Player, self).__init__()
        self.onPlayBackStarted()
        time.sleep(0.4)
        self.onPlayBackPaused()
        self.onPlayBackResumed()
        self.onPlayBackStopped()

    def onPlayBackStarted(self):
        pass

    def onPlayBackEnded(self):
        pass

    def onPlayBackStopped(self):
        pass

    def onPlayBackPaused(self):
        pass

    def onPlayBackResumed(self):
        pass

    def isPlayingVideo(self):
        return True

    def getTime(self):
        return 71

    def getTotalTime(self):
        return 100

    def getPlayingFile(self):
        return ""
        