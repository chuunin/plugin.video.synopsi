import roman
import unittest
import logging
import sys
import SocketServer
import socket
import threading
import time

import default
import xbmc
import xbmcgui
import xbmcaddon

logging.basicConfig(level=logging.DEBUG,
                    format='%(name)s: %(message)s',
                    )

class EchoRequestHandler(SocketServer.BaseRequestHandler):
    
    def __init__(self, request, client_address, server):
        self.logger = logging.getLogger('EchoRequestHandler')
        self.logger.debug('__init__')
        SocketServer.BaseRequestHandler.__init__(self, request, client_address, server)
        return

    def setup(self):
        self.logger.debug('setup')
        return SocketServer.BaseRequestHandler.setup(self)

    def handle(self):
        self.logger.debug('handle')

        # Echo the back to the client
        data = self.request.recv(1024)
        self.logger.debug('handle {0}'.format(str(data)))
        self.logger.debug('recv()->"%s"', data)
        self.request.send(data)
        return

    def finish(self):
        self.logger.debug('finish')
        return SocketServer.BaseRequestHandler.finish(self)

NOTIFY_DATA = ""

class NotificationHandler(SocketServer.BaseRequestHandler):
    
    def __init__(self, request, client_address, server):
        self.logger = logging.getLogger('NotificationHandler')
        self.logger.debug('__init__')
        SocketServer.BaseRequestHandler.__init__(self, request, client_address, server)
        return

    def setup(self):
        self.logger.debug('setup')
        return SocketServer.BaseRequestHandler.setup(self)

    def handle(self):
        self.request.send(NOTIFY_DATA)
        return

    def finish(self):
        self.logger.debug('finish')
        return SocketServer.BaseRequestHandler.finish(self)


class EchoServer(SocketServer.TCPServer):
    
    def __init__(self, server_address, handler_class=EchoRequestHandler):
        self.logger = logging.getLogger('EchoServer')
        self.logger.debug('__init__')
        SocketServer.TCPServer.__init__(self, server_address, handler_class)
        return

    def server_activate(self):
        self.logger.debug('server_activate')
        SocketServer.TCPServer.server_activate(self)
        return

    def serve_forever(self):
        self.logger.debug('waiting for request')
        self.logger.info('Handling requests, press <Ctrl-C> to quit')
        while True:
            self.handle_request()
        return

    def handle_request(self):
        self.logger.debug('handle_request')
        return SocketServer.TCPServer.handle_request(self)

    def verify_request(self, request, client_address):
        self.logger.debug('verify_request(%s, %s)', request, client_address)
        return SocketServer.TCPServer.verify_request(self, request, client_address)

    def process_request(self, request, client_address):
        self.logger.debug('process_request(%s, %s)', request, client_address)
        return SocketServer.TCPServer.process_request(self, request, client_address)

    def server_close(self):
        self.logger.debug('server_close')
        return SocketServer.TCPServer.server_close(self)

    def finish_request(self, request, client_address):
        self.logger.debug('finish_request(%s, %s)', request, client_address)
        return SocketServer.TCPServer.finish_request(self, request, client_address)

    def close_request(self, request_address):
        self.logger.debug('close_request(%s)', request_address)
        return SocketServer.TCPServer.close_request(self, request_address)

def run_fake_api():
    address = ('localhost', 9090) # let the kernel give us a port
    # server = EchoServer(address, EchoRequestHandler)
    ip, port = server.server_address # find out what port we were given

    t = threading.Thread(target=server.serve_forever)
    t.setDaemon(True) # don't hang on exit
    t.start()

    logger = logging.getLogger('client')
    logger.info('Server on %s:%s', ip, port)

    # while True:
    #     pass
    time.sleep(1000)



    logger.debug('closing socket')
    #s.close()
    logger.debug('done')
    server.socket.close()


# logger = logging.getLogger('client')

# def start_fake_api(Handler):
#     address = ('localhost', 9090) # let the kernel give us a port
#     # server = EchoServer(address, EchoRequestHandler)
#     server = EchoServer(address, Handler)
#     ip, port = server.server_address # find out what port we were given

#     t = threading.Thread(target=server.serve_forever)
#     t.setDaemon(True) # don't hang on exit
#     t.start()

#     # logger = logging.getLogger('client')
#     logger.info('Server on %s:%s', ip, port)

# def stop_fake_api():
#     logger.debug('closing socket')
#     #s.close()
#     logger.debug('done')
#     server.socket.close()


class FakeAPI(object):
    """
    docstring for FakeAPI
    """
    def __init__(self):
        super(FakeAPI, self).__init__() 

    def start_fake_api(self, Handler):
        address = ('localhost', 9090) # let the kernel give us a port
        # server = EchoServer(address, EchoRequestHandler)
        self.server = EchoServer(address, Handler)
        ip, port = self.server.server_address # find out what port we were given

        t = threading.Thread(target=self.server.serve_forever)
        t.setDaemon(True) # don't hang on exit
        t.start()

        self.logger = logging.getLogger('client')
        self.logger.info('Server on %s:%s', ip, port)

    def stop_fake_api(self):
        self.logger.debug('closing socket')
        #s.close()
        self.logger.debug('done')
        self.server.socket.close()

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


class StartAddon(unittest.TestCase):
    """
    Test starting addon.
    """ 
    def setUp(self):
        #self.api = FakeAPI()
        # self.api = FalseAPI()
        # self.api.start_fake_api(NotificationHandler)
        #self.api.start_fake_api(EchoRequestHandler)
        pass
        # FalseAPI().run()

    def test_start_stop(self):
        NOTIFY_DATA = '{"jsonrpc":"2.0", "method":"System.OnQuit", "params":{"data":null, "sender":"xbmc"}}'
        #start_fake_api(NotificationHandler)
        #time.sleep(10)
        default.main()
        #stop_fake_api()
    
    def tearDown(self):
        pass
        QUITING = False
        #self.api.stop_fake_api()

if __name__ == "__main__":
    unittest.main()