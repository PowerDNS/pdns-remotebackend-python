"""Unix connector module"""

import os, os.path
import sys
import json
from pdns.remotebackend import Connector

if sys.version_info < (3, 0):
    import SocketServer
else:
    import socketserver
    SocketServer = socketserver # backward compability for python2

class UnixRequestHandler(SocketServer.StreamRequestHandler, Connector):
    """Class implementing unix read/write server"""
    def handle(self):
        """Handle connection"""
        h = self.server.rpc_handler()
        if 'ttl' in self.server.rpc_options:
            h.ttl = self.server.rpc_options['ttl']

        if (self.server.rpc_options["abi"] == 'pipe'):
            return self.mainloop3(self.rfile, self.wfile, h)
        else:
            return self.mainloop4(self.rfile, self.wfile, h)

class UnixConnector(Connector):
    """Connector class, which spawns a server and handler. Provide option path for constructor."""
    def run(self):
        """Start listening in options['path'] and spawn handler per connection. Your remotebackend handler class is rebuilt between connections."""
        if 'path' in self.options:
            path = self.options['path']
        else:
            path = '/tmp/remotebackend.sock'
        if os.path.exists(path):
            os.remove(path)

        s = SocketServer.UnixStreamServer(path, UnixRequestHandler, False)
        s.rpc_handler = self.handler
        s.rpc_options = self.options
        s.server_bind()
        s.server_activate()
        try:
            s.serve_forever()
        except (KeyboardInterrupt, SystemExit):
            pass
        os.remove(path)
