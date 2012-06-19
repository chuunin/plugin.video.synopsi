import lib
from urllib2 import HTTPError

print lib.hashFile('C:\Users\Tommy\Videos\Season 6\How.I.Met.Your.Mother.S06E09.HDTV.XviD-LOL.[VTV].avi')

print lib.url_fix('http://de.wikipedia.org/wiki/Elf (Begriffsklrung)')

print lib.url_fix('SELECT COUNT (idMovie) FROM Movie')

#print lib.get_token("ferko","jurko")

print lib.get_token("virgl@synopsi.tv","asdasd")

try:
    print lib.get_token("ferko","jurko")
except HTTPError, e:
    if e.code == 400:
        print "Ble"
