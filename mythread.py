import threading
import logging

class MyThread(threading.Thread):
	def __init__(self):
		super(MyThread, self).__init__()
		self.name = self.__class__.__name__
		self._log = logging.getLogger(self.name)
		fh = logging.FileHandler(os.path.join('log', self.name + '.log'))
		self._log.addHandler(fh)

