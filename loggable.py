import logging
import logging.handlers
import os

class Loggable(object):
	lognames = []
	
	def __init__(self):
		self.name = self.get_log_name()
		self._log = logging.Logger(self.name)
		self._log.setLevel(logging.DEBUG)
		# assure that log dir exists
		#~ print('cwd ' + os.getcwd())
		logdir = os.path.join(os.getcwd(), 'log')
		#~ print('path exists' + str(os.path.exists(logdir)))
		if not os.path.exists(logdir):
			#~ print 'creating log'
			os.mkdir(logdir)

		fh = logging.handlers.RotatingFileHandler(os.path.join('log', self.name + '.log'), mode='w', backupCount=2)
		self._log.addHandler(fh)

		# try to add handlers from default log
		def_log = logging.getLogger()
		#~ self._log.debug('default logger\'s handler count %d' % len(def_log.handlers))
		self._log.handlers += def_log.handlers

	def get_log_name(self):
		new_log_name = self.__class__.__name__
		if new_log_name in self.lognames:
			new_log_name += '_' + str(id(self))
		else:	
			self.lognames.append(new_log_name)
			
		return new_log_name
		
