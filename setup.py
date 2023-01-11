#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup and build script for the library."""

from setuptools import setup, find_packages

CLASSIFIERS = [
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.7',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Multimedia :: Sound/Audio',
    'Topic :: Multimedia :: Sound/Audio :: Players',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
]

setup(
    name="DeeFuzzer",
    url="http://github.com/yomguy/DeeFuzzer",
    description="open, light and instant media streaming tool",
    long_description=open('README.rst').read(),
    author="Guillaume Pellerin",
    author_email="yomguy@parisson.com",
    version='0.8.2',
    install_requires=[
        'setuptools',
        'wheel',
        'python-shout==0.2.7',
        'python-twitter==3.5',
        'mutagen==1.45.1',
        'pyliblo3==0.12.0',
        'pycurl==7.44.1',
        'pyyaml==5.4.1',
        'mysqlclient==2.0.3',
    ],
    platforms=['OS Independent'],
    license='GPL v3',
    scripts=['scripts/deefuzzer'],
    classifiers=CLASSIFIERS,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    python_requires='>=3',
)
