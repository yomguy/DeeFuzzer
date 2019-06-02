.. image:: https://github.com/yomguy/DeeFuzzer/raw/master/doc/img/logo_deefuzzer.png

|version| |downloads| |travis_master|

.. |travis_master| image:: https://secure.travis-ci.org/yomguy/DeeFuzzer.png?branch=master
    :target: https://travis-ci.org/yomguy/DeeFuzzer/

.. |version| image:: https://img.shields.io/pypi/v/DeeFuzzer.svg
  :target: https://pypi.python.org/pypi/DeeFuzzer/
  :alt: Version

.. |downloads| image:: https://img.shields.io/pypi/dm/DeeFuzzer.svg
    :target: https://pypi.python.org/pypi/DeeFuzzer/
    :alt: Downloads


DeeFuzzer is a light and instant application for streaming audio and video over internet.
It is dedicated to communities who wants to easily create web radios, web TVs,
live multimedia relays or personal home radios, with metadata management and cool features.


Features
========

 * Streaming MP3, OGG Vorbis files over Internet
 * Live streaming for any kind of format (WebM compatible)
 * Full metadata encapsulation and management
 * Recursive folders, random or M3U playlists management
 * M3U, RSS and JSON podcast generators for URLs, current tracks and playlists
 * Automagic mountpoint creation based on media subfolders
 * Multiple station streaming with only one config file
 * Auto twitting #nowplaying tracks
 * Auto jingling between tracks
 * OSC controller for a few commands
 * Very light and optimized streaming process
 * Fully written in Python
 * Works with Icecast2, ShoutCast, Stream-m
 * (NEW) Works with MySQL playlists

Because our aim is to get DeeFuzzer as light as possible it is NOT capable of re-encoding or transcoding media files for the moment.


News
====

0.7.2

 * Add MySQL module and connection routine to get the playlist from a database (thanks to doomy23)
 * Prepare the Python3 switch
 * Tested against libshout 2.4.1 and python-shout 0.2.1
 * As been used in relay mode in production for almost 5000+ hours
 * Improve conf YAML format support

0.7.1

 * Bugfix release
 * Fix no metadata for stream-m relaying

0.7

 * **Huge** refactoring which should be compatible with old setups, but before updating **please read** the `updated example <https://github.com/yomguy/DeeFuzzer/blob/dev/example/deefuzzer_doc.xml>`_ and the following news.
 * Reworked the RSS feed handling to allow JSON output as well and more configuration options (@achbed #27 #28)
 * Add an init.d script to act as a deamon (@achbed)
 * Add stationdefaults preference (apply default settings to all stations) (@achbed #31)
 * Add stationfolder preference (generate stations automatically from a folder structure) (@achbed #31)
 * Add stationconfig preference (load other preference files as stations) (@achbed #31)
 * Add new station.server.appendtype option
 * Add new base_dir parameter to station definition
 * Better thread management (@achbed #36 #37 #38)
 * Improved stability avoiding crashes with automatic station restart methods (@achbed #39 #45)
 * Added option (ignoreerrors) to log and continue when an error occurs during station initialization (@achbed #43)
 * Cleanup, better documentation and good ideas (@ChoiZ #15 #16 #17 #23)
 * Various bugfixes
 * Many thanks to all participants and especially to @achbed for his **huge** work, efficiency and easy collaboration
 * Enjoy!

0.6.6

 * Update station name (remove ": http://url")
 * Update mountpoint name (remove .mp3 or .ogg)
 * Update metadata (replace " : " by " - " between Artist and Track)
 * Remove "ogg_quality" on mp3 streams

0.6.5

 * Stable WebM live streaming through Stream-m server
 * Read yaml configuration files
 * Read m3u playlist files
 * Minor fixes


Installation
============

DeeFuzzer has now only been well tested on Linux, but should work on any other platform.
You would then need to install libshout3 and liblo libraries for it. On Windows,
an install inside Gygwin should work well.

To install it, say on Debian, do::

    sudo apt-get install python-pip python-dev python-liblo \
                         python-mutagen python-pycurl python-yaml \
                         libshout3-dev librtmp-dev liblo-dev \
                         libcurl4-openssl-dev libmysqlclient-dev

Now update distribute and setuptools::

    sudo pip install -U distribute setuptools

Then::

    sudo pip install deefuzzer

To upgrade::

    sudo pip install -U deefuzzer

If you have some version problems with the installation, please also try in a virtualenv.

As a streaming client, the DeeFuzzer needs a local or remote streaming server like Icecast2 to do something::

    sudo apt-get install icecast2


Usage
=====

deefuzzer CONFIGFILE

where CONFIGFILE is the path for a XML or YAML config file. For example::

    deefuzzer example/deefuzzer.xml

or::

    deefuzzer example/deefuzzer.yaml

To make the deefuzzer act as a deamon, just play it in the background::

    deefuzzer example/deefuzzer.yaml &

Note that you must edit the config file with right parameters before playing.


Documentation
=============

 * `FAQ and Wiki <https://github.com/yomguy/DeeFuzzer/wiki>`_
 * `API <http://files.parisson.com/doc/deefuzzer/>`_
 * `Documented XML configuration <https://github.com/yomguy/DeeFuzzer/blob/master/example/deefuzzer_doc.xml>`_
 * Configuration examples:

     * `Dummy XML for testing <https://github.com/yomguy/DeeFuzzer/blob/master/example/deefuzzer.xml>`_
     * `Generic YAML <https://github.com/yomguy/DeeFuzzer/blob/master/example/deefuzzer.yaml>`_


Development
===========

Everybody is welcome to participate to the DeeFuzzer project!

We use GitHub to collaborate: https://github.com/yomguy/DeeFuzzer

Clone it, star it and join us!


Authors
=======

 * @yomguy +GuillaumePellerin yomguy@parisson.com
 * @achbed +achbed github@achbed.org
 * @ChoiZ +FrançoisLASSERRE choiz@me.com


License
=======

This software is released under the terms of the CeCILL license (GPLv2 compatible).
as described in the file LICENSE.txt in the source directory or online https://github.com/yomguy/DeeFuzzer/blob/master/LICENSE.txt


Aknowledgements
===============

This work is inspired by the great - C coded - Oddsock's streaming program: Ezstream.
Since I needed to patch it in order to modify the playlist (randomize for example)
and make external batch tools to create multiple channels, I decided to rewrite it
from scratch in python.

Some parts of this work are also taken from another Parisson's project: Telemeta
(see http://telemeta.org).


Contact / Infos
===============

Twitter: @yomguy @parisson_studio
Expertise, Business, Sponsoring: http://parisson.com
