import requests
import json

r = requests.get('http://localhost:9099/?q=The+Holy+Grail')
if r.text[0] == '{':
	print json.dumps(json.loads(r.text), indent=4)
else:
	print r.text
