import lib, time, os

class Timer():
    def __enter__(self):
        self.start = time.time()

    def __exit__(self, *args):
        print str(time.time() - self.start)
# with Timer():
# 	print "1"
# 	print lib.myhash("C:\Users\Tommy\Videos\Iron.Sky.2012.XviD.700MB.avi")
# # print lib.myhash("C:\Users\Tommy\Videos\Iros.Sky.2012.XviD.700MB.avi")

# with Timer():
# 	print "2"
# 	print lib.old_stv_hash("C:\Users\Tommy\Videos\Iron.Sky.2012.XviD.700MB.avi")

# with Timer():
# 	print "3"
# 	print lib.stv_hash("C:\Users\Tommy\Videos\Iron.Sky.2012.XviD.700MB.avi")

# with Timer():
# 	for _file in os.listdir("C:\Users\Tommy\Videos\Season 7"):
# 		print _file
# 		print lib.stv_hash("C:\\Users\\Tommy\\Videos\\Season 7\\" + _file)

import os

for dirname, dirnames, filenames in os.walk('.'):
    for subdirname in dirnames:
        print os.path.join(dirname, subdirname)
    for filename in filenames:
        print os.path.join(dirname, filename)