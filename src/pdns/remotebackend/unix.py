"""Unix connector module"""

import os
import os.path
import sys

from pdns.remotebackend import Connector

if sys.version_info < (3, 0):
    import SocketServer
else:
    import io
    import socketserver
    SocketServer = socketserver  # backward compability for python2


class UnixRequestHandler(SocketServer.StreamRequestHandler, Connector):
    """Class implementing unix read/write server"""
    def handle(self):
        """Handle connection"""
        options = self.server.rpc_options
        with self.server.rpc_handler(options=options) as h:
            if sys.version_info < (3, 0):
                rfile = self.rfile
                wfile = self.wfile
            else:
                rfile = io.TextIOWrapper(
                    self.rfile, encoding="utf-8", newline="\n"
                )
                wfile = io.TextIOWrapper(
                    self.wfile, encoding="utf-8", newline="\n"
                )

            if (options["abi"] == 'pipe'):
                return self.mainloop3(rfile, wfile, h)
            else:
                return self.mainloop4(rfile, wfile, h)


class ThreadedUnixStreamServer(SocketServer.ThreadingMixIn,
                               SocketServer.UnixStreamServer):
    pass


class UnixConnector(Connector):
    """Connector class, which spawns a server and handler.
       Provide option path for constructor."""
    def run(self):
        """Start listening in options['path'] and spawn handler per connection.
           Your remotebackend handler class is rebuilt between connections."""
        if 'path' in self.options:
            path = self.options['path']
        else:
            path = '/tmp/remotebackend.sock'
        if os.path.exists(path):
            os.remove(path)

        s = ThreadedUnixStreamServer(path, UnixRequestHandler, False)
        s.rpc_handler = self.handler
        s.rpc_options = self.options
        s.server_bind()
        s.server_activate()
        try:
            s.serve_forever()
        except (KeyboardInterrupt, SystemExit):
            pass
        os.remove(path)
