import pdns.remotebackend, pdns.remotebackend.unix
import sys
import io

class MyHandler(pdns.remotebackend.Handler):
    def do_lookup(self,args):
        if (args['qname'] == 'test.com' and args['qtype'] in ('ANY', 'A')):
            self.result = []
            self.result.append(self.record_prio_ttl('test.com','A','127.0.0.1',0,300))
        if (args['qname'] == 'test.com' and (args['qtype'] in ('ANY', 'SOA'))):
            self.result = []
            self.result.append(self.record_prio_ttl('test.com','SOA','sns.dns.icann.org. noc.dns.icann.org. 2013073082 7200 3600 1209600 3600',0,300))

pdns.remotebackend.PipeConnector(MyHandler, {"abi":sys.argv[1]}).run()
