import msgpack, platform, pyinotify, requests, utmp, config
from utmp.reader import UTmpRecordType
from util import get_uid

class EventHandler(pyinotify.ProcessEvent):
	def process_IN_MODIFY(self, event):
		upload()

def parse_utmp(path):
	logins = []
	with open(path, 'rb') as fd:
		buf = fd.read()
		for entry in utmp.read(buf):
			if entry.type == UTmpRecordType.user_process:
				logins.append(entry)
	return logins

def record_to_dict(record):
	login = {
		'host': platform.node(),
		'user': record.user,
		'uid': get_uid(record.user),
		'rhost': record.host,
		'line': record.line,
		'time': record.sec,
	}
	return login

def upload():
	logins = parse_utmp(config.utmp_file)
	login_list = []

	for login in logins:
		login_list.append(record_to_dict(login))

	data = msgpack.packb(login_list)
	requests.put(config.server_endpoint, data=data,
	             auth=(platform.node(), config.password))

def main():
	upload()

	wm = pyinotify.WatchManager()
	notifier = pyinotify.Notifier(wm, EventHandler())
	wm.add_watch(config.utmp_file, pyinotify.IN_MODIFY)
	notifier.loop()

if __name__ == '__main__':
	main()

