#!/usr/bin/env python

from distutils.core import setup

setup(
    name='Pdns_Remotebackend',
    version='0.3',
    description='Support package for PowerDNS remotebackend',
    long_description='This package is intended to make writing remotebackends with python easier. It provides base class for request handling and connector classes for pipe and unix connectors.',
    author='Aki Tuomi',
    author_email='cmouse@cmouse.fi',
    url='https://github.com/cmouse/pdns-remotebackend-python',
    license='MIT',
    platforms=['all'],
    packages=['pdns','pdns.remotebackend'],
    package_dir={'pdns.remotebackend': 'src/pdns/remotebackend',
                 'pdns':'src/pdns'},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: Name Service (DNS)',
    ],               
)
