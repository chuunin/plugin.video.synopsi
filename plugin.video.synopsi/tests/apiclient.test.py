import os, sys

# if __name__ == "__main__" and __package__ is None:
#     __package__ = "tests/apiclient.test"

sys.path.insert(0, os.path.abspath('..'))

print sys.path

#import apiclient
from apiclient import apiclient
#apiclient = __import__('apiclient')


base_url = 'http://neptune.local:8000/'
key = '76ccb5ec8ecddf15c29c5decac35f9'
secret = '261029dbbdd5dd481da6564fa1054e'
username = 'martin.smid@gmail.com'
password = 'aaa'

client = apiclient(base_url, key, secret, username, password, debugLvl = 0)
client.getAccessToken()
client.titleWatched(2848299, 'like')


