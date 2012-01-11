#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''The setup and build script for the python-twitter library.'''

import os

__version__ = '0.6.1'
__author__ = 'yomguy@parisson.com'

# The base package metadata to be used by both distutils and setuptools
METADATA = dict(
  name = "DeeFuzzer",
  version = __version__,
  py_modules = ['deefuzzer'],
  description='an easy and instant media streaming tool',
  author='Guillaume Pellerin',
  author_email='yomguy@parisson.com',
  license='CeCILL',
  url='http://svn.parisson.org/deefuzzer',
  keywords='audio video streaming broadcast shout',
  install_requires = ['setuptools', 'tinyurl', 'python-shout', 'python-twitter', 'mutagen', 'pyliblo', 'pycurl'],
  packages=['deefuzzer', 'deefuzzer.tools'],
  include_package_data = True,
  scripts=['scripts/deefuzzer'],
  classifiers = ['Programming Language :: Python', 'Topic :: Internet :: WWW/HTTP :: Dynamic Content', 'Topic :: Multimedia :: Sound/Audio', 'Topic :: Multimedia :: Sound/Audio :: Players',],
  long_description=open('README.rst').read(),
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
