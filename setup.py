#!/usr/bin/env python

from distutils.core import setup

setup(name='Pdns_Remotebackend',
      version='0.1',
      description='Support class for PowerDNS remotebackend',
      author='Aki Tuomi',
      author_email='cmouse@cmouse.fi',
      url='https://github.com/cmouse/pdns-remotebackend-python',
      packages=['pdns.remotebackend'],
      package_dir={'pdns.remotebackend': 'src/pdns/remotebackend'},
     )
