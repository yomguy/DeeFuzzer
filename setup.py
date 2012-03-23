#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''The setup and build script for the python-twitter library.'''

import os
import deefuzzer

README = os.path.join(os.path.dirname(__file__), 'README.rst')

# The base package metadata to be used by both distutils and setuptools
METADATA = dict(
  name = "DeeFuzzer",
  version = deefuzzer.__version__,
  py_modules = ['deefuzzer'],
  description='an open, light and instant media streaming tool',
  author='Guillaume Pellerin',
  author_email='yomguy@parisson.com',
  license='CeCILL',
  url='http://github.com/yomguy/DeeFuzzer',
  keywords='media audio video streaming broadcast shout',
  install_requires = ['setuptools', 'tinyurl', 'python-shout', 'python-twitter', 'mutagen', 'pyliblo', 'pycurl'],
  packages=['deefuzzer', 'deefuzzer.tools'],
  include_package_data = True,
  scripts=['scripts/deefuzzer'],
  classifiers = ['Programming Language :: Python', 'Topic :: Internet :: WWW/HTTP :: Dynamic Content', 'Topic :: Multimedia :: Sound/Audio', 'Topic :: Multimedia :: Sound/Audio :: Players',],
  long_description=open(README).read(),
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
