import socket, json, time, sys

custom = {
	'add_video_source': [
		'Input.Select',
		'Input.SendText /home/smid/Videos/Movies',
		# 'Input.Select',
		'Input.Down',
		'Input.SendText Movies',
		'Input.Down',
	]
}


def call_method(methodName, params = {}):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect(('127.0.0.1', 9899))
	
	req = {
		'id': 1,
		'jsonrpc': '2.0',
		'method': methodName,
		'params': params
	}
	
	# print json.dumps(req)
	
	s.sendall(json.dumps(req))
	strdata = s.recv(1024)
	s.close()

	data = json.loads(strdata)
	if not data.get('result') == 'OK':
		print '=' * 20
		print 'Received', repr(data)
		print '=' * 20

def handle_command_line(line):
	print line
	# ignore empty lines
	if not len(line):
		return
	# ignore comments
	if line[0] == '#':
		return
	elif line == '@stop':
		raise Exception('stopped')
	else:
		l = line.split()
		if not len(l):
			return

		call_method(l[0], l[1:])



if __name__ == '__main__':
	a1 = sys.argv[1]
	fname =  os.path.join(os.getcwd(), sys.argv[1])

	if a1[0] == '@':
		batch = custom[a1[1:]]
	else:
		print 'opening ' + sys.argv[1]
		f = open(fname)
		batch = f.read().splitlines()	

	for line in batch:
		handle_command_line(line)
		time.sleep(0.2)
