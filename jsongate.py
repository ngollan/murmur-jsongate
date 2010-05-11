#!/usr/bin/env python

import Ice, sys, os

from murmur import Murmur
from murmur.json.authenticator import ServerAuthenticatorI

httpconn = False

def add_authenticator(server, adapter):
	server_authenticator = Murmur.ServerAuthenticatorPrx.uncheckedCast(adapter.addWithUUID(ServerAuthenticatorI(server, adapter)))
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
