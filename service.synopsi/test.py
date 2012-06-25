import lib
from urllib2 import HTTPError
import json

print lib.hashFile('C:\Users\Tommy\Videos\Season 6\How.I.Met.Your.Mother.S06E09.HDTV.XviD-LOL.[VTV].avi')
print lib.hashFile2('C:\Users\Tommy\Videos\Season 6\How.I.Met.Your.Mother.S06E09.HDTV.XviD-LOL.[VTV].avi')


#print lib.get_token("ferko","jurko")
"""
print lib.get_token("virgl@synopsi.tv","asdasd")

try:
    print lib.get_token("ferko","jurko")
except HTTPError, e:
    if e.code == 400:
        print "Ble"
"""

j = '{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": {"properties": ["file","imdbnumber"]}, "id": 1}'

print json.loads(j)
properties =['file', 'imdbnumber']
method = 'VideoLibrary.GetMovies'
#limits=
dic = {'params': {'properties': properties, 'limits': {'end': 5, 'start': 0 }},
       'jsonrpc': '2.0',
       'method': method,
       'id': 1}

print json.dumps(dic)
"""
'limits': { /* id: List.Limits, no additional properties allowed */
            'end': -1 /* integer, minimum: 0, The number of items in the list being returned */, 
            'start': 0 /* integer, minimum: 0 */
        }
"""

print lib.myhash('C:\Users\Tommy\Videos\Season 6\How.I.Met.Your.Mother.S06E09.HDTV.XviD-LOL.[VTV].avi')
