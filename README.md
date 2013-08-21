pdns-remotebackend-python
=========================

This package is intended to help with remotebackend scripts. 

Installation
------------
To install, run 

```
python setup.py build
python setup.py install
```

Usage
-----

To use, import pdns.remotebackend, and subclass Handler. This code
currently supports Pipe and Unix Connector, which you can use.

Example
--­----

```
import pdns.remotebackend, pdns.remotebackend.unix
import sys
import io

class MyHandler(pdns.remotebackend.Handler):
    def do_lookup(self,args):
        if (args['qname'] == 'test.com' and args['qtype'] == 'ANY'):
            self.result = []
            self.result.append(self.record_prio_ttl('test.com','A','127.0.0.1',0,300))
        if (args['qname'] == 'test.com' and (args['qtype'] == 'ANY' or args['qtype'] == 'SOA')):
            self.result = []
            self.result.append(self.record_prio_ttl('test.com','A','127.0.0.1',0,300))
            self.result.append(self.record_prio_ttl('test.com','SOA','sns.dns.icann.org. noc.dns.icann.org. 2013073082 7200 3600 1209600 3600',0,300))

if __name__ == 'main'
	pdns.remotebackend.PipeConnector(MyHandler).run()
# or you can use
#	pdns.remotebackend.unix.UnixConnector(MyHandler).run()
```

Details
---
The Handler class will call your class with do_<api function>. initialize becomes do_initialize. The function is passed a hash with all the keys provided. 
Please see http://doc.powerdns.com/html/remotebackend.html for details on the API. 

Connector constructor is 

 Connector(HandlerClass, options = {})

Supported options for all connectors is ttl, which defines default ttl to use if missing. For Unix Connector you can also specify path, which is path to the
unix socket file to use. 
