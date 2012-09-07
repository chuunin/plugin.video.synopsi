import unittest
import service
import SocketServer
import time
import threading

from tests import xbmc, xbmcgui, xbmcaddon

def PrepareTests():
    pass

def NotificationTests(request):
    # {"jsonrpc":"2.0","method":"VideoLibrary.OnUpdate","params":{"data":{"item":{"id":48,"type":"episode"}},"sender":"xbmc"}}
    request.send('{"jsonrpc":"2.0","method":"VideoLibrary.OnUpdate","params":{"data":{"item":{"id":48,"type":"episode"}},"sender":"xbmc"}}')
    time.sleep(0.05)
    request.send('{"jsonrpc":"2.0","method":"VideoLibrary.OnRemove","params":{"data":{"id":2,"type":"episode"},"sender":"xbmc"}}')
    time.sleep(0.05)
    request.send('{"jsonrpc":"2.0","method":"System.OnQuit","params":{"data":null,"sender":"xbmc"}}')

def MethodTests():
    pass

class EchoRequestHandler(SocketServer.BaseRequestHandler):
    def setup(self):
        print self.client_address, 'connected'
        NotificationTests(self.request)

    def handle(self):
        data = 'dummy'
        while data:
            data = self.request.recv(1024)
            self.request.send(data)
            if data.strip() == 'bye':
                return

    def finish(self):
        print self.client_address, 'disconnected'

HOST, PORT = "localhost", 9090
SERVER = SocketServer.TCPServer((HOST, PORT), EchoRequestHandler)
class TCPServer(threading.Thread):
    def __init__(self):
        super(TCPServer, self).__init__()

    def run(self):
        SERVER.serve_forever()

def main():
    service.main()


if __name__ == '__main__':
    PrepareTests()
    t = TCPServer().start()
    try:
        main()
    except Exception,e:
        SERVER.shutdown()
        raise e
    else: 
        SERVER.shutdown()
