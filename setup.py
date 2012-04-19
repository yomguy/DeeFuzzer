#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''The setup and build script for the library.'''

from setuptools import setup, find_packages
import deefuzzer

CLASSIFIERS = ['Programming Language :: Python',
                'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
                'Topic :: Multimedia :: Sound/Audio',
                'Topic :: Multimedia :: Sound/Audio :: Players',]

setup(
  name = "DeeFuzzer",
  url = "http://github.com/yomguy/DeeFuzzer",
  description = "an open, light and instant media streaming tool",
  long_description = open('README.rst').read(),
  author = "Guillaume Pellerin",
  author_email = "yomguy@parisson.com",
  version = deefuzzer.__version__,
  install_requires = [
        'setuptools',
        'tinyurl',
        'python-shout',
        'python-twitter',
        'mutagen',
        'pyliblo',
        'pycurl',
  ],
  platforms=['OS Independent'],
  license='CeCILL v2',
  scripts=['scripts/deefuzzer'],
  classifiers = CLASSIFIERS,
  packages = find_packages(),
  include_package_data = True,
  zip_safe = False,
)
