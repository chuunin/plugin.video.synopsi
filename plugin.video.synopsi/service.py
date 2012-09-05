"""
This is default file of SynopsiTV service. See addon.xml
<extension point="xbmc.service" library="service.py" start="login|startup">
"""
from library import Library
from scrobbler import Scrobbler

def main():
    Library().start()
    Scrobbler().start()

if __name__ == "__main__":
    main()
