import mythread
import traceback

from addon_utilities import *

class AddonService(mythread.MyThread):
    def __init__(self, host, port, apiClient):
        super(AddonService, self).__init__()
        self.host = host        # Symbolic name meaning all available interfaces
        self.port = port        # Arbitrary non-privileged port
        self.apiClient = apiClient

    def run(self):
        self._log.debug('ADDON SERVICE / Thread start')
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        s.bind((self.host, self.port))
        s.listen(1)
        self._log.debug('SERVICE / Listening on %s:%d' % (self.host, self.port))

        while not xbmc.abortRequested:
            try:
                conn, addr = s.accept()
            except:
                continue
                
            self._log.debug('Accepted connection from %s' % str(addr))
            data = ""
            
            # receive data
            while not xbmc.abortRequested:
                data_chunk = conn.recv(1024)
                if not data_chunk: break
                data += data_chunk

            conn.close()

            self._log.debug('SERVICE / RECV / ' + str(data))

            # parse data
            try:
                json_data = json.loads(data)
            except:
                self._log.debug('Invalid data "%s"' % str(data))
                continue

            try:
                # handle requested method
                methodName = json_data['command']
                arguments = json_data.get('arguments', {})

                method = getattr(self, methodName)
                method(arguments)
            except Exception as e:
                # raise
                self._log.error('ERROR CALLING METHOD "%s": %s' % (methodName, str(e)))
                self._log.error('TRACEBACK / ' + traceback.format_exc)

        self._log.debug('ADDON SERVICE / Thread end')

    def show_categories(self, arguments):
        show_categories(**arguments)


    def show_movies(self, arguments):
        show_movies(self.apiClient, **arguments)

