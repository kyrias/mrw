from flask import Flask, request, g, Response
from auth import requires_auth
import datetime, msgpack, os.path, sqlite3

app = Flask(__name__)
app.config.from_object('config')

insert_query = '''INSERT INTO utmp (host, user, uid, rhost, line, time, updated)
                    VALUES (:host, :user, :uid, :rhost, :line, :time, :updated)'''
delete_query = '''DELETE FROM utmp WHERE host = ?'''


def init_db():
	with app.app_context():
		db = connect_db()
		with app.open_resource('schema.sql', mode='r') as f:
			db.cursor().executescript(f.read())
		db.commit()
		db.close()

def connect_db():
	db_path = app.config['DATABASE']
	return sqlite3.connect(db_path)


@app.before_request
def before_request():
	g.db = connect_db()
	g.db.row_factory = sqlite3.Row

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


def dict_from_rows(rows):
	'''Convert a list of sqlite3.Row to a list of dicts'''
	l = []
	for row in rows:
		l += [dict(zip(row.keys(), row))]
	return l


@app.route('/update', methods=['PUT'])
@requires_auth(check_auth)
def update():
	'''API endpoint for submitting utmp data to

	:return: status code 400 - unsupported Content-Type
	:return: status code 200 - successful submission
	'''

	hostname = request.authorization.username
	if request.headers['content-type'] == 'application/x-msgpack':
		logins = msgpack.unpackb(request.data, encoding='utf-8')
	else:
		return Response(status=400)

	update_utmp(g.db, hostname, logins)
	return Response('Update successful for host {}'.format(hostname), status=200)

@app.route('/list')
def list():
	rows = g.db.cursor().execute("SELECT * FROM utmp").fetchall()
	logins = dict_from_rows(rows)

	best_mimetype = request.accept_mimetypes.best
	if best_mimetype == 'application/x-msgpack':
		return Response(msgpack.packb(logins), 200,
		                {'Content-Type': 'application/x-msgpack'})


if __name__ == '__main__':
	db_path = app.config['DATABASE']
	if not os.path.isfile(db_path):
		init_db()

	app.run(port=app.config['PORT'])
