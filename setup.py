#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''The setup and build script for the python-twitter library.'''

import os
from distutils.core import setup
from deefuzzer import __version__

__author__ = 'yomguy@parisson.com'
    
# The base package metadata to be used by both distutils and setuptools
METADATA = dict(
  name = "DeeFuzzer",
  version = __version__,
  py_modules = ['deefuzzer'],
  description='an easy and instant media streaming tool',
  author='Guillaume Pellerin', 
  author_email='yomguy@parisson.com',
  license='License.txt',
  url='http://svn.parisson.org/deefuzzer',
  keywords='audio video streaming broadcast shout',
  install_requires = ['setuptools', 'tinyurl', 'python-shout', 'python-twitter'],
  packages=['deefuzzer', 'deefuzzer.tools'], 
  include_package_data = True,
  scripts=['scripts/deefuzzer'], 
  classifiers = ['Programming Language :: Python', 'Topic :: Internet :: WWW/HTTP :: Dynamic Content', 'Topic :: Multimedia :: Sound/Audio', 'Topic :: Multimedia :: Sound/Audio :: Players',],
  long_description=open('README.txt').read(),
)

def Main():
  # Use setuptools if available, otherwise fallback and use distutils
  try:
    import setuptools
    setuptools.setup(**METADATA)
  except ImportError:
    import distutils.core
    distutils.core.setup(**METADATA)
    
if __name__ == '__main__':
    Main()
