import requests
import json
import sys

print sys.argv

if len(sys.argv) == 1:
	r = requests.get('http://localhost:9099/search/?q=The+Holy+Grail')
elif sys.argv[1] == 'detail':
	r = requests.get('http://localhost:9099/get_detail/?q=%s' % sys.argv[2])
else:
	r = requests.get('http://localhost:9099/search/?q=%s' % sys.argv[1])

# print result
if r.text[0] == '{':
	print json.dumps(json.loads(r.text), indent=4)
else:
	print r.text
