#!/usr/bin/env python
#
# Short demo for the Ice-to-JSON callback gateway. It will just sit there
# and try to send authentication and information requests to an HTTP server
# on localhost:10000, which likely means you get an error message every time
# a user logs in to a server.
#
# To set the Slice file location, make sure the environment variable
# MURMUR_SLICE_PATH is set correctly (default: '/usr/share/slice/Murmur.ice'
# which should work on Debian-based Linux distributions).
#
# This code is based on Chris Heald's implementation of 'comet-server',
# available as part of murmur-manager:
#            http://github.com/cheald/murmur-manager

import Ice, sys, os

from murmur import Murmur
from murmur.json.authenticator import ServerAuthenticatorI

def add_authenticator(server, adapter):
	authenticator = ServerAuthenticatorI(server, adapter)
	authenticator.base_uri = 'http://localhost:10000/'

	server_authenticator = Murmur.ServerAuthenticatorPrx.uncheckedCast(adapter.addWithUUID(authenticator))
	server.setAuthenticator(server_authenticator)

class MetaCallbackI(Murmur.MetaCallback):
	def started(self, s, current=None):
		add_authenticator(s, current.adapter)

	def stopped(self, s, current=None):
		pass

if __name__ == "__main__":
	ice = Ice.initialize(sys.argv)
	meta = Murmur.MetaPrx.checkedCast(ice.stringToProxy('Meta:tcp -h 127.0.0.1 -p 6502'))
	adapter = ice.createObjectAdapterWithEndpoints("Callback.Client", "tcp -h 127.0.0.1")
	adapter.activate()
	for server in meta.getBootedServers():
		add_authenticator(server, adapter)

	try:
		ice.waitForShutdown()
	except KeyboardInterrupt:
		print 'Interrupt caught, exiting'

	ice.shutdown()
