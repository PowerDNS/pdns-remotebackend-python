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
currently supports Pipe and Unix Connector, which you can use. This version
also supports pipe backend, you can signify this by setting option 'abi' to pipe.

Example
-------

```
import pdns.remotebackend, pdns.remotebackend.unix
import sys
import io

class MyHandler(pdns.remotebackend.Handler):
    def do_lookup(self, qname='', qtype='', **kwargs):
        self.result =  []
        self.log.append("Handling a new DNS request")
        if (qname == 'test.com' and qtype == 'ANY'):
            self.result.append(self.record('test.com','A','127.0.0.1',ttl=300))
        if (qname == 'test.com' and (qtype == 'ANY' or qtype == 'SOA')):
            self.result.append(self.record('test.com','A','127.0.0.1',ttl=300))
            self.result.append(self.record('test.com','SOA','sns.dns.icann.org. noc.dns.icann.org. 2013073082 7200 3600 1209600 3600',ttl=300))

if __name__ == '__main__':
	pdns.remotebackend.PipeConnector(MyHandler).run()
# or you can use
#	pdns.remotebackend.unix.UnixConnector(MyHandler).run()
```

Details
---
The Handler class will call your class with do\_\<api function\>. initialize becomes do\_initialize. The function is passed a hash with all the keys provided. 
Please see http://doc.powerdns.com/html/remotebackend.html for details on the API. 

All log messages will appear in the PowerDNS log. For the messages to appear, the PowerDNS log level needs to be set to 6 or above.

Connector constructor is 
```
Connector(HandlerClass, options = {})
```
Supported options for all connectors is ttl, which defines default ttl to use if missing. For Unix Connector you can also specify path, which is path to the
unix socket file to use. 
