import logging
import sys
import SocketServer
import socket
import threading


abortRequested = False

def sleep(time):
    pass

def log(string):
    print string

def executeJSONRPC(json):
    pass

def executebuiltin(builtin):
    pass

class Player(object):
    def __init__(self):
        super(Player, self).__init__()

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
        