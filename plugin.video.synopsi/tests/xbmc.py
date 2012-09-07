import logging
import sys
import SocketServer
import socket
import threading
import time
import json


abortRequested = False

def sleep(time):
    pass


def log(string):
    print string


def executeJSONRPC(js):
    print "XBMC recieved: ", js.strip()
    return "{}"
    # data = json.loads(js)
    # for key in data.keys():
    #     if "VideoLibrary" in key:
    #         print js


def executebuiltin(builtin):
    pass


class Player(object):
    def __init__(self):
        super(Player, self).__init__()
        self.onPlayBackStarted()
        self.onPlayBackPaused()
        self.onPlayBackResumed()
        self.onPlayBackEnded()

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
        return "70"

    def getTotalTime(self):
        return "100"

    def getPlayingFile(self):
        return ""
        