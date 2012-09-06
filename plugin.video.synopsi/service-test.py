import unittest
# import service
import SocketServer
import time
import threading

class MyTCPHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        print "{} wrote:".format(self.client_address[0])
        print self.data
        # just send back the same data, but upper-cased
        self.request.sendall(self.data.upper())

HOST, PORT = "localhost", 9090
SERVER = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)
class TCPServer(threading.Thread):
    def __init__(self):
        super(TCPServer, self).__init__()

    def run(self):
        SERVER.serve_forever()

def main():
    print "Sleeping"
    # time.sleep(1)


if __name__ == '__main__':
    t = TCPServer().start()
    main()
    SERVER.shutdown()