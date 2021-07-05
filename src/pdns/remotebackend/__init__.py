"""PowerDNS remotebackend support module"""
import json
import re
import sys
import traceback

VERSION = "0.7.2"
"""Module version string"""


class Handler:
    """Base class for request handler, you have to implement at least do_lookup.
       Please see
       http://doc.powerdns.com/html/remotebackend.html#remotebackend-api
       for information on how to implement anything. All methods get called
       with hash containing the request variables."""

    description = "PowerDNS python remotebackend"
    version = VERSION

    def __init__(self, options={}):
        """Initialize with default values"""
        self.log = []
        """Array of log messages"""
        self.result = False
        """Result of the invocation"""
        self.ttl = 300
        """Default TTL"""
        self.params = {}
        """Any handler parameters you want to store"""
        self.options = options
        """Connector options"""

        if 'ttl' in self.options:
            self.ttl = self.options['ttl']

    def record(self, qname, qtype, content, ttl=-1, auth=1):
        """Generate one record"""
        if ttl == -1:
            ttl = self.ttl
        return {'qtype': qtype, 'qname': qname, 'content': content,
                'ttl': ttl, 'auth': auth}

    def do_initialize(self, *args):
        """Default handler for initialization method, stores any parameters
           into attribute params"""
        self.params = args
        self.log.append(
            "{0} version {1} initialized".format(
                self.description, self.version
            )
        )
        self.result = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass


class Connector:
    """Connector base class for handling endless loop"""
    def __init__(self, klass, options={}):
        # initialize the handler class
        self.handler = klass
        """"Handler class"""
        self.options = options
        """Any options"""
        if "abi" not in self.options:
            self.options["abi"] = 'remote'

    def mainloop(self, reader, writer):
        """Setup basic reader/writer and start correct main loop"""
        with self.handler(options=self.options) as h:
            if self.options["abi"] == 'pipe':
                return self.mainloop3(reader, writer, h)
            else:
                return self.mainloop4(reader, writer, h)

    def mainloop3(self, reader, writer, h):
        """Reader/writer and request de/serialization for pipe backend"""
        # initialize
        line = reader.readline()
        m = re.match("^HELO\t([1-4])", line)
        if m is not None:
            # simulate empty initialize
            h.do_initialize({})
            writer.write(
                "OK\t{0} version {1} initialized\n".format(
                    h.description, h.version
                )
            )
            writer.flush()
            self.abi = int(m.group(1))
        else:
            writer.write("FAIL\n")
            writer.flush()
            while(True):
                line = reader.readline()
                if line == "":
                    return

        # keep track of last seen SOA for AXFR
        last_soa_name = None

        while(True):
            line = reader.readline().strip().split("\t")
            if not line:
                break
            if (len(line) < 2):
                break
            h.log = []
            h.result = False
            method = line[0]
            parms = {}

            if method == "AXFR":
                parms = {"zonename": last_soa_name, "domain_id": int(line[1])}
                method = "do_list"
            elif method == "Q":
                parms = {
                    "qname": line[1],
                    "qclass": line[2],
                    "qtype": line[3],
                    "domain_id": int(line[4]),
                    "zone_id": int(line[4]),
                    "remote": line[5]
                }
                if self.abi > 1:
                    parms["local"] = line[6]
                if self.abi > 2:
                    parms["edns-subnet"] = line[7]
                if (line[3] == "SOA"):
                    last_soa_name = line[1]
                method = "do_lookup"
            else:
                writer.write("FAIL\n")
                writer.flush()
                continue

            if (callable(getattr(h, method, None))):
                getattr(h, method)(parms)

            if (len(h.log) > 0):
                writer.write("LOG\t{0}\n".format(h.log[0]))

            if not isinstance(h.result, bool):
                for r in h.result:
                    if "scopeMask" not in r:
                        r["scopeMask"] = 0
                    if "domain_id" not in r:
                        r["domain_id"] = int(parms["domain_id"])
                    if (self.abi < 3):
                        writer.write(
                            "DATA\t{0}\t{1}\t{2}\t{3}\t{4}\t{5}\n".format(
                                r["qname"], "IN", r["qtype"], r["ttl"],
                                r["domain_id"], r["content"]
                            )
                        )
                    else:
                        writer.write(
                            "DATA\t{0}\t{1}\t{2}\t{3}\t{4}\t"
                            "{5}\t{6}\t{7}\n".format(
                                r["scopeMask"], r["auth"], r["qname"], "IN",
                                r["qtype"], r["ttl"], r["domain_id"],
                                r["content"]
                            )
                        )
                writer.write("END\n")
            else:
                writer.write("FAIL\n")

            writer.flush()

    def mainloop4(self, reader, writer, h):
        """Reader/writer and request de/serialization for remotebackend"""

        while(True):
            line = reader.readline()
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
                writer.write(json.dumps({'result': h.result, 'log': h.log}))
            except ValueError:
                writer.write(json.dumps({'result': False,
                                         'log': ["Cannot parse input"]}))
            # errors are never visible if we don't catch this exception.
            except BaseException:
                writer.write(json.dumps({'result': False,
                                         'log': [traceback.format_exc()]}))

            writer.write("\n")
            writer.flush()


class PipeConnector(Connector):
    """Pipe Connector"""
    def run(self):
        """Startup pipe connector with stdin/stdout as source/sink"""
        try:
            self.mainloop(sys.stdin, sys.stdout)
        except (KeyboardInterrupt, SystemExit):
            pass
