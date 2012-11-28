# python standart lib
import threading
import logging
import os

# application
import loggable


class MyThread(threading.Thread, loggable.Loggable):
	def __init__(self):
		super(MyThread, self).__init__()
		self.name = self.__class__.__name__
