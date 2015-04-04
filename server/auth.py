from flask import Response, request
from functools import wraps

def authenticate():
	"""Sends a 401 response that enables basic auth"""
	return Response('Could not verify your access level for that URL.\n'
	                'You have to login with proper credentials', 401,
	                {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(check_auth):
	def decorator(func):
		@wraps(func)
		def decorated(*args, **kwargs):
			auth = request.authorization
			if not auth or not check_auth(auth.username, auth.password):
				return authenticate()
			return func(*args, **kwargs)
		return decorated
	return decorator

