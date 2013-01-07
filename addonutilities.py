# xbmc
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

# python standart lib
import urllib
import sys
import os
import time
import json
import re
import os.path
import logging
import traceback
import subprocess
from datetime import datetime
import CommonFunctions
import socket

# application
from app_apiclient import AppApiClient, AuthenticationError
from utilities import *
from cache import StvList, DuplicateStvIdException
from xbmcrpc import xbmc_rpc


#~ def get_local_tvshows():
	#~ localtvshows = xbmc_rpc.get_all_tvshows()
	#~ log(dump(localtvshows))
#~ 
	#~ return [ { 'name': item['label'], 'cover_medium': item['thumbnail'] } for item in localtvshows['tvshows'] ]

