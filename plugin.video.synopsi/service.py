"""
This is default file of SynopsiTV service. See addon.xml
<extension point="xbmc.service" library="service.py" start="login|startup">
"""
from scrobbler import Scrobbler
from library import Library

def main():
    
	s = Scrobbler()
	s.start()

	Library().start()

if __name__ == "__main__":
	main()
