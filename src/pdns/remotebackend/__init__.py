"""PowerDNS remotebackend support module"""
import json,sys,io,re,os

VERSION="0.3"
"""Module version string"""

class Handler:
    """Base class for request handler, you have to implement at least do_lookup. 
       Please see http://doc.powerdns.com/html/remotebackend.html#remotebackend-api for information 
       on how to implement anything. All methods get called with hash containing the request variables."""
    def __init__(self):
        """Inititalize with default values"""
        self.log = []
        """Array of log messages"""
        self.result = False
        """Result of the invocation"""
        self.ttl = 300
        """Default TTL"""
        self.params = {}
        """Any handler parameters you want to store"""

    def record_prio_ttl(self, qname, qtype, content, prio, ttl, auth=1):
        """Generate one record without any defaults"""
        return {'qtype': qtype, 'qname': qname, 'content': content, 
                'ttl': ttl, 'auth': auth}
    
    def record_prio(self, qname, qtype, content, prio, auth=1):
        """Generate one record with default ttl"""
        return self.record_prio_ttl(qname, qtype, content, prio, self.ttl, auth)

    def record(self, qname, qtype, content, auth=1):
        """Generate one record with default ttl and prio (0)"""
        return self.record_prio(qname, qtype, content, 0, auth)
    
    def do_initialize(self, *args):
        """Default handler for initialization method, stores any parameters into attribute params"""
        self.params = args
        self.log.append("PowerDNS python remotebackend version {0} initialized".format(VERSION))
        self.result = True

class Connector:
    """Connector base class for handling endless loop"""
    def __init__(self, klass, options = {}):
        self.handler = klass # initialize the handler class
        """"Handler class"""
        self.options = options
        """Any options"""
        if ("abi" in self.options) == False:
            self.options["abi"] = 'remote'

    def mainloop(self, reader, writer):
        """Setup basic reader/writer and start correct main loop"""
        h = self.handler()
        if 'ttl' in self.options:
            h.ttl = options['ttl']
        if self.options["abi"] == 'pipe':
            return self.mainloop3(reader, writer, h)
        else:
            return self.mainloop4(reader, writer, h)

    def mainloop3(self, reader, writer, h):
        """Reader/writer and request de/serialization for pipe backend"""
        h = self.handler()
        if 'ttl' in self.options:
            h.ttl = options['ttl']

        # initialize
        line = reader.readline()
        m = re.match("^HELO\t([1-3])", line)
        if m != None:
            writer.write("OK\tPowerDNS python remotebackend version {0} initialized\n".format(VERSION))
            writer.flush()
            self.abi = int(m.group(1))
        else:
            writer.write("FAIL\n");
            writer.flush()
            while(True):
                line = reader.readline()
                if line == "":
                    return
        
        # keep track of last seen SOA for AXFR
        last_soa_name = None

        while(True):
            line = reader.readline().split("\t")
            if (len(line) < 2):
                break
            h.log = []
            h.result = False
            method = line[0]
            parms = {}

            if method == "AXFR":
                parms = {"zonename":last_soa_name, "domain_id":int(line[1])}
                method = "do_list"
            elif method == "Q":
                parms = {"qname":line[1], "qclass":line[2], "qtype":line[3], "domain_id":int(line[4]), "zone_id":int(line[4]), "remote":line[5]}
                if self.abi == 2:
                    parms["local"] = line[6]
                if self.abi == 3:
                    parms["edns-subnet"] = line[7]
                if (line[3] == "SOA"):
                    last_soa_name = line[1]
                method = "do_lookup"
            else:
                writer.write("FAIL\n")
                writer.flush()
                continue

            if (callable(getattr(h, method, None))):
                getattr(h,method)(parms)

            if (h.result != False):
                for r in h.result:
                    if ("scopeMask" in r) == False:
                        r["scopeMask"] = 0
                    if ("domain_id" in r) == False:
                        r["domain_id"] = int(parms["domain_id"])
                    if (self.abi < 3):
                        writer.write("DATA\t{0}\t{1}\t{2}\t{3}\t{4}\t{5}\n".format(r["qname"], "IN", r["qtype"], r["ttl"], r["domain_id"], r["content"]))
                    else:
                        writer.write("DATA\t{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\n".format((r["scopeMask"], r["auth"], r["qname"], "IN", r["qtype"], r["ttl"], r["domain_id"], r["content"])))

                writer.write("END\n")
            else:
                writer.write("FAIL\n")

            if (len(h.log) > 0):
                writer.write("LOG\t{0}\n".format(h.log[0]))
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
                    getattr(h,method)(args)
                writer.write(json.dumps({'result':h.result,'log':h.log}))
            except ValueError:
                writer.write(json.dumps({'result':False,'log':"Cannot parse input"}))
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
