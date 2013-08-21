import os, os.path
import sys
import json
from pdns.remotebackend import Connector

if sys.version_info < (3, 0):
    import SocketServer
else:
    import socketserver

class UnixRequestHandler(SocketServer.StreamRequestHandler):
    def handle(self):
        h = self.server.rpc_handler()
        if 'ttl' in self.server.rpc_options:
            h.ttl = self.server.rpc_options['ttl']

        while(True):
            line = self.rfile.readline()
            if line == "":
                break
            try:
                data_in = json.loads(line)
                method = "do_{0}".format(data_in['method'].lower())
                args = {}
                if ('parameters' in data_in):
                    args = data_in['parameters']
                h.result = False
                h.log = []
                if (callable(getattr(h, method, None))):
                    getattr(h, method)(args)
                self.wfile.write(json.dumps({'result':h.result,'log':h.log}) + "\n")
            except ValueError:
                self.wfile.write(json.dumps({'result':False,'log':"Cannot parse input"}) + "\n")

class UnixConnector(Connector):
    def run(self):
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
        except KeyboardInterrupt, SystemExit:
            pass
        os.remove(path)
