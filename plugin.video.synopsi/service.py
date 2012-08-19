"""
This is default file of SynopsiTV service.
"""
from library import Library
from scrobbler import Scrobbler

def main():
    Library().start()
    Scrobbler().start()

if __name__ == "__main__":
    main()
