from flask import Flask, request, g, Response
from auth import requires_auth
import sqlite3, msgpack, datetime

app = Flask(__name__)
app.config.from_object('config')

insert_query = '''INSERT INTO utmp (host, user, uid, rhost, line, time, updated)
                         VALUES (:host, :user, :uid, :rhost, :line, :time, :updated)'''
delete_query = '''DELETE FROM utmp WHERE host = ?'''

def connect_db():
	return sqlite3.connect(app.config['DATABASE'])

@app.before_request
def before_request():
	g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
	db = getattr(g, 'db', None)
	if db is not None:
		db.close()


def check_auth(hostname, password):
	if hostname in app.config['CREDENTIALS']:
		return password == app.config['CREDENTIALS'][hostname]
	else:
		return False


def update_utmp(db, hostname, logins):
	cursor = db.cursor()
	cursor.execute(delete_query, (hostname,))
	for login in logins:
		login['updated'] = int(datetime.datetime.now().timestamp())
		cursor.execute(insert_query, login)
	db.commit()


@app.route('/update', methods=['PUT'])
@requires_auth(check_auth)
def update():
	hostname = request.authorization.username
	logins = msgpack.unpackb(request.data, encoding='utf-8')
	update_utmp(g.db, hostname, logins)
	return 'Update successful for host {}'.format(hostname)


if __name__ == '__main__':
	app.run(port=app.config['PORT'])
