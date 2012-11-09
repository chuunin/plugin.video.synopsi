import threading
from addon_utilities import *

class AddonService(threading.Thread):
    def __init__(host, port):
        super(AddonService, self).__init__()
        self.host = host        # Symbolic name meaning all available interfaces
        self.port = port        # Arbitrary non-privileged port
        self._log = logging.getLogger()

    def run():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.host, self.port))
        s.listen(1)
        
        while 1:
            conn, addr = s.accept()
            self._log.debug('Accepted connection from ', addr)
            # receive data
            while 1:
                data = conn.recv(1024)
                if not data: break
            conn.close()

            # parse data
            
            # handle requested method
            
            method = getattr(self, methodName)
            method(arguments)


