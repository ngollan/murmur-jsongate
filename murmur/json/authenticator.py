#!/usr/bin/env python

from .. import Murmur
import httplib, json, base64, urllib2

class UserNotFoundError(Exception):
	def __init__(self, value):
		self.value = value

	def __str__(self):
		return repr(self.value)

RET_FALLTHROUGH = (-2, "", [])
RET_DENIED = (-1, "", [])

class ServerAuthenticatorI(Murmur.ServerAuthenticator):
	"""Authenticator implementation

	Converts the Ice authentication calls to JSON and tries to resolve them via
	a web service. I just hope this works well with the blocking nature of
	the calls. Better hook it up to a responsive backend.

	TODO: API token support
	TODO: Texture retrieval (delayed until I have at least a basic working
	      auth server)
	"""

	def __init__(self, server, adapter):
		self.server = server

		self.base_uri = "http://localhost:9000/"
		self.known_user_info = ('UserName', 'UserEmail', 'UserComment', 'UserHash', 'UserPassword')
		self.auth_api_token = "Just Made It Up"


	def authenticate(self, name, pw, certificates, certhash, certstrong, current=None):
		"""Returns ID (0, -1, -2), newname, groups

		Map to: POST mumble/auth
		"""

		request_string = json.write({
			"name": name,
			"password": pw,
			"certificates": map(lambda c: base64.b64encode(c), certificates),
			"certhash": certhash,
			"certstrong": certstrong
		})

		user_info = None

		try:
			req = urllib2.Request(url="%s%s" % (self.base_uri, 'mumble/auth'), data=request_string, headers={"Content-Type": "application/json"})
			f = urllib2.urlopen(url=req)
			user_info = json.read(f.read())
		except urllib2.URLError, e:
			print "Could not connect to authentication server: %s, falling through." % e.reason
			return RET_FALLTHROUGH
		except urllib2.HTTPError, e:
			if e.code == httplib.UNAUTHORIZED:
				print "Authentication failed for user %s, access denied." % name
				return RET_DENIED
			else:
				print "Unhandled authentication server response %d, falling through." % he.code
				return RET_FALLTHROUGH
		except json.ReadException:
			print "Server returned invalid JSON as authentication response, falling through."
			return RET_FALLTHROUGH
		else:
			print "Something weird happened while talking to the authentication server, falling through."
			return RET_FALLTHROUGH

		if not (isinstance(user_info, dict) and 'id' in user_info):
			print "Authentication server did not return a valid dict, falling through."
			return RET_FALLTHROUGH

		newname = ""
		groups = []

		if 'newname' in user_info and isinstance(user_info['newname'], str):
			newname = user_info['newname']

		if 'groups' in user_info and isinstance(user_info['groups'], list):
			groups = filter(lambda g: isinstance(g, str), user_info['groups'])

		return (user_info['id'], newname, groups)

	def get_user_info(self, id):
		"""Fetch a dict of all user info from the server.

		id: either numerical or a name (will be URL encoded)

		Returns a dict of all available user information, or throws a
		UserNotFoundErrors if the user doesn't exist.

		Map to: mumble/users/(id).json
		"""

		user_info = None

		try:
			f = urllib2.urlopen(url="%s%s%s.json" % (self.base_uri, 'mumble/users/', urllib2.quote("%s" % id, '')))
			user_info = json.read(f.read())
		except urllib2.URLError, e:
			print "Could not connect to authentication server: %s" % e.reason
		except urllib2.HTTPError, e:
			print "Unhandled authentication server response %d." % he.code
		except json.ReadException:
			print "Server returned invalid JSON as user information."
		else:
			print "Something weird happened while retrieving user data."

		if not (isinstance(user_info, dict) and 'id' in user_info and 'name' in user_info):
			raise UserNotFoundError("Could not retrieve user information for %s" % id)

		return user_info

	def getInfo(self, id, current=None):
		"""Return (true/false) depending on availability of information, plus
		a dictionary of user information."""

		try:
			return (True, dict(filter(lambda (k,v): k in self.known_user_info, get_user_info(id).items())))

		except UserNotFoundError:
			return (False, {})

	def nameToId(self, name, current=None):
		"""Return ID of a given user, -2 if unknown."""

		try:
			user_info = get_user_info(id)
			return user_info['id']

		except UserNotFoundError:
			return -2

	def idToName(self, id, corrent=None):
		"""Return the name of a given user ID, empty string means unknown ID."""

		try:
			user_info = get_user_info(id)
			return user_info['name']

		except UserNotFoundError:
			return ""


	def idToTexture(self, id, corrent=None):
		"""Return the texture as a raw bytestream.

		Map to: mumble/users/(id)/avatar

		TODO: stubbed out for now
		"""

		return []
