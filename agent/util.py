import pwd

def get_uid(username):
	user = pwd.getpwnam(username)
	return user.pw_uid
