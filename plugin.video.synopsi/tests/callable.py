class noneCall(object):
	def __call__(self):
		pass

class Fake(object):

	def __init__(self, what):
		self.what = what
		print what, 'x'

	def __getattr__(self, methodName):
		try:
			method = getattr(m, methodName)
			print method
		except:
			print 'Undefined method:' + methodName
			return noneCall

		return method

class Methods(object):
	def __init__(self):
		pass

	def Gama(self, someValue):
		print someValue

  

m = Methods()

f = Fake('a')
f.ble()
f.Gama('huh')

