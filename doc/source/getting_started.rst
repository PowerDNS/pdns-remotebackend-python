***************
Getting started
***************

Quickstart script
=================

.. code-block:: python

  import pdns.remotebackend
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
              self.result.append(self.record_prio_ttl('test.com','SOA','sns.dns.icann.org noc.dns.icann.org 2013073082 7200 3600 1209600 3600',0,300))

  pdns.remotebackend.PipeConnector(MyHandler).run()


PowerDNS configuration
======================

To use the script with PowerDNS, add following lines into configuration:

.. line-block::
  launch=remote
  remote-connection-string=pipe:command=/path/to/script.py

Implementing methods
====================

You can find a list of methods that are supported by remotebackend from http://doc.powerdns.com/html/remotebackend.html#remotebackend-api. To implement these, you must write a do\_ method for them. 

.. function::do_lookup(self, args) 

To return a result, you set self.result into array of returns values, True, or whatever else is expected. This will gets rendered into json. Default result is always False. You *must* set result on success.


To push log messages into PowerDNS, you can add them into self.log. 

:samp:`self.log << "Hello, world"`
