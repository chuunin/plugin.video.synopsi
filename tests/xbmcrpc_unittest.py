# python standart lib
import os, sys
from unittest import *
import logging
import json

# test helper
from common import connection

sys.path.insert(0, os.path.abspath('..'))

# application
from xbmcrpc import xbmc_rpc

# test
from utilities import *


class XbmcRPCTest(TestCase):
	def test_get_movie_details(self):
		movie_details = xbmc_rpc.get_movie_details(1)
		print dump(movie_details)

	def test_save_details(self):
		details = {
			'movieid': 1,
			'title': 'Movie Title',
			'playcount': 5,
			'runtime': 110,
			'director': ['Director Igor'],
			'studio': ['Studio'],
			'year': 1984,
			'plot': 'plot',
			'genre': ['An Imaginary Genre', 'Comedy'],
			'rating': 11,
			'mpaa': 'mpaa',
			'imdbnumber': 'imdbnumber',
			'votes': 'votes',
			'lastplayed': 'lastplayed',
			'originaltitle': 'originaltitle',
			'trailer': 'trailer',
			'tagline': 'tagline',
			'plotoutline': 'plotoutline',
			'writer': ['Writer'],
			'country': ['Country', 'Country 2'],
			'top250': 210,
			'sorttitle': 'sorttitle',
			'set': 'set',
			'showlink': ['showlink'],
			'thumbnail': 'thumbnail',
			'fanart': 'fanart',
			'tag': ['tag'],
			# 'cast': ['Jozko Pucik', 'Jano Mak'], 
			# 'streamdetails': '', 
			# 'file': '', 
			# 'resume': '', 
			# 'setid': '',  
			# 'dateadded': '', 
			# 'art': {}			# todo
		}
		
		res = xbmc_rpc.set_movie_details(details)

	def test_translate_stv2xbmc(self):
		stv_title = {
			'id': 1,
			'type': 'movie',
			'name': 'Rambo'
		}

		items = translate_stv2xbmc(stv_title)


if __name__ == '__main__':
	test_item1 = {
		'type': 'movie',
		'id': 10,
		'file': '/var/log/virtual.ext',
		'stvId': 10009,
		'stv_title_hash': 'ba7c6a7bc6a7b6c',
	}

	#~ c = connection
	#~ apiClient = ApiClient(c['base_url'], c['key'], c['secret'], c['username'], c['password'], c['device_id'], debugLvl=logging.ERROR, rel_api_url=c['rel_api_url'])
	cwd = os.path.join(os.getcwd(), 'cache.dat')

	#~ cache = StvList(c['device_id'], apiClient, cwd)

	logger = logging.getLogger()

	if len(sys.argv) < 2:
		suite = TestLoader().loadTestsFromTestCase(XbmcRPCTest)
	else:
		suite = TestLoader().loadTestsFromName('XbmcRPCTest.' + sys.argv[1], sys.modules[__name__])

	TextTestRunner(verbosity=2).run(suite)
