import logging
import sys
import SocketServer
import socket
import threading
import time


QUITING = False
class FalseAPI(threading.Thread):
    """
    docstring for FalseAPI
    """
    def __init__(self):
        super(FalseAPI, self).__init__()

    def run(self):
        pass
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind(("localhost", 9090))
        self.s.listen(1)
        self.conn, self.addr = self.s.accept()
        print 'Connected by', self.addr
        while not QUITING:
            data = self.conn.recv(1024)
            if not data: break
            self.conn.sendall(data)
        self.conn.close()

def main():
    FalseAPI().run()

if __name__ == "__main__":
    main()