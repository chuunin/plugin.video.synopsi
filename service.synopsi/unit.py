import unittest
import default

	

class DeviceIDTest(unittest.TestCase):
    """
    Test wheter device_id is same.
    """ 

    def test_dev_id(self):
        dev_id = default.generate_deviceid()
        for i in xrange(1,10):
        	self.assertEqual(dev_id, default.generate_deviceid())


class SendTest(unittest.TestCase):
	"""
	docstring for SendTest
	"""
	
	def test_good_token(self):
		default.TrySendData({},"d727b89ee2")

	def test_bad_token(self):
		default.TrySendData({},"d727b89eee")

class LoginTest(unittest.TestCase):
	"""
	docstring for SendTest
	"""
	
	def test_bad_login(self):
		default.login("asd","asd")

class HashTest(unittest.TestCase):
	"""
	docstring for SendTest
	"""
	def hash(self, num_bytes):
		f = open('test/workfile', 'w')
		for i in xrange(num_bytes):
			f.write('0')
		f.close()
		# print default.get_hash_array("test/workfile")
		return default.get_hash_array("test/workfile")

	def test_toosmall(self):
		SIZES = (100, 128)
		for i in SIZES:
			self.assertEqual(0, len(self.hash(i)))

	def test_only_synopsihash(self):
		SIZES = (256, 512, 1024, 256*256)
		for i in SIZES:
			self.assertEqual(1, len(self.hash(i)[0]))

	def test_both(self):
		SIZES = (512 ** 2, 512 * 513)
		for i in SIZES:
			self.assertEqual(2, len(self.hash(i)[0]))


	def test_non_existing(self):
		self.assertEqual(0, len(default.get_hash_array("teads.png")))

	# def test_more_filesizes(self):
	# 	for i in xrange(250, 512 * 513):
	# 		if i < 256:
	# 			self.assertEqual(0, len(self.hash(i)))
	# 		elif i < 512 ** 2:
	# 			self.assertEqual(1, len(self.hash(i)[0]))
	# 		else:
	# 			self.assertEqual(2, len(self.hash(i)[0]))

if __name__ == "__main__":
    unittest.main()
