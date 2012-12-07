# python standart lib
import os, sys
from unittest import *
import logging
import json

# test helper
from common import connection

# application
sys.path.insert(0, os.path.abspath('..'))
from utilities import *
from apiclient import *
from cache import StvList

class UtilitiesTest(TestCase):
	def test_hashes(self):
		def gethash(path):
			movie = {}
			movie['stv_title_hash'] = stv_hash(path)
			movie['os_title_hash'] = hash_opensubtitle(path)
			return movie
		
		print gethash('/home/smid/Videos/TVShows/How.I.Met.Your.Mother/anything.s02e10.avi')


if __name__ == '__main__':
	test_item1 = {
		'type': 'movie',
		'id': 10,
		'file': '/var/log/virtual.ext',
		'stvId': 10009
	}		
		
		

	logger = logging.getLogger()

	if len(sys.argv) < 2:
		suite = TestLoader().loadTestsFromTestCase(UtilitiesTest)
	else:
		suite = TestLoader().loadTestsFromName('UtilitiesTest.' + sys.argv[1], sys.modules[__name__])
		
	TextTestRunner(verbosity=2).run(suite)


