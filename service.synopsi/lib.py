"""
This file is obsolete. It will be rewritten soon.
"""

import struct
import os
import urllib
import urlparse
import hashlib
import json

from base64 import b64encode
from urllib import urlencode
from urllib2 import Request, urlopen

# definitions of properties
KEY = 'd0198f911ef0292c83850f9dd77a5a'
SECRET = '69884a55080284e41937e7a007e522'
# data = {
# 'grant_type':'password', 
# 'client_id': key,
# 'client_secret': secret,
# 'username': 'virgl@synopsi.tv', 
# 'password': 'asdasd'
# }

HTTP_HEADERS = {
            'AUTHORIZATION': 'BASIC %s' % b64encode("%s:%s" % (KEY, SECRET)),
            'user-agent': 'linux'
}


def get_token(user, passwd):
    """
    Get oauth token.
    """
    data = {
    'grant_type':'password',
    'client_id': KEY,
    'client_secret': SECRET,
    'username': user,
    'password': passwd
    }
    response = urlopen(Request('http://dev.synopsi.tv/oauth2/token/', 
        data=urlencode(data), 
        headers=HTTP_HEADERS, origin_req_host='dev.synopsi.tv'
    ))
    response_json = json.loads(response.readline())

    access_token = response_json['access_token']
    # refresh_token = response_json['refresh_token']
    # Permanent token
    # return (access_token, refresh_token)

    return (access_token, "")


def send_data(json_data, access_token):
    """
    Send data.
    """
    # example of sending data
    # json_data = {'test': 'example'}
    data = {
    'client_id': KEY,
    'client_secret': SECRET,
    'bearer_token': access_token,
    'data': json.dumps(json_data)
    }
    
    response = urlopen(Request('http://dev.synopsi.tv/api/desktop/',
        data=urlencode(data),
        headers=HTTP_HEADERS, origin_req_host='dev.synopsi.tv'
    ))


def myhash(filepath):
    """
    TODO: Rename to stv_hash.   
    """

    sha1 = hashlib.sha1()

    try:
        with open(filepath, 'rb') as f:
            sha1.update(f.read(256))
            f.seek(-256, 2)
            sha1.update(f.read(256))
    except (IOError) as e:
        return None
    
    return sha1.hexdigest()


def hashFile(name):
    """
    OpenSubtitles hash.
    """
    try:
        longlongformat = 'q'  # long long 
        bytesize = struct.calcsize(longlongformat) 
         
        _file = open(name, "rb")
              
        filesize = os.path.getsize(name) 
        hash = filesize
              
        if filesize < 65536 * 2:
            return None
            # return "SizeError" 
             
        for x in range(65536 / bytesize): 
            _buffer = _file.read(bytesize) 
            (l_value,) = struct.unpack(longlongformat, _buffer)  
            hash += l_value 
            hash = hash & 0xFFFFFFFFFFFFFFFF #to remain as 64bit number  

        _file.seek(max(0, filesize - 65536), 0)
        for x in range(65536 / bytesize):
            _buffer = _file.read(bytesize) 
            (l_value,)= struct.unpack(longlongformat, _buffer)  
            hash += l_value 
            hash = hash & 0xFFFFFFFFFFFFFFFF 

        _file.close()
        returnedhash =  "%016x" % hash 
        
        return returnedhash 

    except(IOError):
        return None
        # return "IOError"