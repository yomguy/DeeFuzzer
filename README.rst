.. image:: https://github.com/yomguy/DeeFuzzer/raw/master/doc/img/logo_deefuzzer.png

|version| |downloads| |travis_master|

.. |travis_master| image:: https://secure.travis-ci.org/yomguy/DeeFuzzer.png?branch=master
    :target: https://travis-ci.org/yomguy/DeeFuzzer/

.. |version| image:: https://pypip.in/version/DeeFuzzer/badge.png
  :target: https://pypi.python.org/pypi/DeeFuzzer/
  :alt: Version

.. |downloads| image:: https://pypip.in/download/DeeFuzzer/badge.svg
    :target: https://pypi.python.org/pypi/DeeFuzzer/
    :alt: Downloads


DeeFuzzer is a light and instant application for streaming audio and video over internet.
It is dedicated to communities who wants to easily create web radios, web TVs,
live multimedia relays or personal home radios, with metadata management and cool features.


Features
========

 * MP3, OGG Vorbis file and live streaming over Internet
 * Full metadata encapsulation and management
 * RSS podcast generator (current tracks and playlists)
 * M3U playlist generator
 * Recursive, random (shuffled) or pre-defined playlists
 * Multi-threaded architecture: multiple station streaming with one config file
 * Auto twitting the current playing track and new tracks
 * Auto jingling between tracks
 * OSC controller: control the main functions from a distant terminal
 * Relaying: relay and stream live sessions!
 * WebM video relaying support
 * Very light and optimized streaming process
 * Fully written in Python
 * Works with Icecast2, ShoutCast, Stream-m

Because our aim is to get DeeFuzzer as light as possible it is NOT capable of re-encoding or transcoding media files for the moment.


News
====

0.7

 * Huge refactoring which should be compatible with old setups, but please read the `updated example <https://github.com/yomguy/DeeFuzzer/blob/dev/example/deefuzzer_doc.xml>`_ before going on
 * Reworked the RSS feed handling to allow JSON output as well and more configuration options (@achbed #27 #28)
 * Add an init.d script to act as a deamon (@achbed)
 * Add stationdefaults preference (apply default settings to all stations) (@achbed #31)
 * Add stationfolder preference (generate stations automatically from a folder structure) (@achbed #31) 
 * Add stationconfig preference (load other preference files as stations) (@achbed #31)
 * Add new station.server.appendtype option
 * Add new base_dir parameter to station definition
 * New stationdefaults parameter (provides a mechanism to give default values for all stations) (@achbed #29)
 * Better thread management (@achbed #36 #37 #38)
 * Improved stability avoiding crashes with automatic station restart methods (@achbed #39 #45)
 * Added option (ignoreerrors) to log and continue when an error occurs during station setup (@achbed #43)
 * Cleanup, better documentation and good ideas (@choiz #15 #16 #17 #23)
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

    sudo apt-get install python-pip python-dev libshout3-dev python-liblo python-mutagen \
                         python-pycurl liblo-dev libshout3-dev librtmp-dev \
                         python-yaml libcurl4-openssl-dev python-mutagen icecast2

Now, the easiest way to install the DeeFuzzer from a shell::

    sudo pip install deefuzzer

To upgrade::

    sudo pip install -U deefuzzer

For more informations, please see on `GitHub <https://github.com/yomguy/DeeFuzzer>`_ or tweet to @yomguy


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
You can find an example for a draft XML file in the "example" directory of the source code.

WARNING: because we need the DeeFuzzer to be a very stable streaming process with multiple channel management,
the multi-threaded implementation of deefuzzer instances avoids shutting down the process with a CTRL+C.
You have to kill them manually, after a CTRL+Z, making this::

    pkill -9 deefuzzer

or, more specificially::

    pkill -9 -f "deefuzzer example/deefuzzer.yaml"


Configuration
=============

Some examples of markup configuration files:

 * `generic and documented XML <https://github.com/yomguy/DeeFuzzer/blob/master/example/deefuzzer_doc.xml>`_
 * `generic XML for testing <https://github.com/yomguy/DeeFuzzer/blob/master/example/deefuzzer.xml>`_
 * `OGG Vorbis and MP3 together <https://github.com/yomguy/DeeFuzzer/blob/master/example/deefuzzer_mp3_ogg.xml>`_
 * `generic YAML <https://github.com/yomguy/DeeFuzzer/blob/master/example/deefuzzer.yaml>`_


OSC Control
===========

Some of the DeeFuzzer function parameters can be control through the great OSC protocol.
The OSC server is only active if the <control><mode> tag is set up to "1"
in the config file (see example/deefuzzer.xml again..).

The available parameters are:

    * playing: next track
    * twitting: start and stop
    * relaying: start and stop
    * jingling: start and stop
    * recording: start and stop

See `examples here. <https://github.com/yomguy/DeeFuzzer/blob/master/scripts/>`_

Then any OSC remote (PureDate, Monome, TouchOSC, etc..) can a become controller! :)

We provide some client python scripts as some examples about how to control the parameters
from a console or any application (see deefuzzer/scripts/).


Twitter (manual and optional)
=============================

To get track twitting, please install python-twitter, python-oauth2 and all their dependencies.

Install or make sure python-oauth2 and python-twitter are installed::

    sudo easy_install oauth2
    sudo pip install python-twitter

As Twitter access requires oauth keys since 07/2010, you need to get your own access token key pair.
Please run the dedicated script to do this from the main deefuzzer app directory::

    python tools/get_access_token.py

You will be invited to copy/paste an URL in your browser to get a pin code.
Then copy/paste this code into the console and press ENTER.
The script gives you a pair of keys: one access token key and one access token secret key.

Change the <twitter> block options in your deefuzzer XML config file, giving the 2 keys.
For example::

    <twitter>
            <mode>1</mode>
            <key>85039615-H6yAtXXCx7NobF5W40FV0c8epGZsQGkE7MG6XRjD2</key>
            <secret>A1YW3llB9H9qVbjH8zOQTOkMlhVqh2a7LnA9Lt0b6Gc</secret>
            <tags>Music Groove</tags>
    </twitter>

Your DeeFuzzer will now tweet the currently playing track and new tracks on your profile.


Station Folders
===============

Station folders are a specific way of setting up your file system so that you can auto-create many stations
based on only a few settings.  The feature requires a single main folder, with one or more subfolders.  Each
subfolder is scanned for the presence of media files (audio-only at the moment).  If files are found, then a
station is created using the parameters in the <stationfolder> block.  Substitution is performed to fill in
some detail to the stationfolder parameters, and all stationdefaults are also applied.

The base folder is specified by the <folder> block.  No substitution is done on this parameter.

Subsitution is done for [name] and [path] - [name] is replaced with the name of the subfolder, and [path] is
replaced with the subfolder's complete path.

Consider the following example.  We have a block with the following settings:

		<stationfolder>
				<folder>/path/to/media</folder>
				<infos>
						<short_name>[name]</short_name>
						<name>[name]</name>
						<genre>[name]</genre>
				</infos>
				<media>
						<dir>[path]</dir>
				</media>
		</stationfolder>

The folder structure is as follows:

		/path/to/media
				+ one
						- song1.mp3
						- song2.mp3
				+ two
						- song3.ogg
				+ three
						- presentation.pdf
				+ four
						- song4.mp3

In this case, three stations are created:  one, two, and four.  Each will have their short name (and thus their
icecast mount point) set to their respective folder names.  Subfolder three is skipped, as there are no audio files
present - just a PDF file.


API
===

http://files.parisson.com/doc/deefuzzer/


Development
===========

Everybody is welcome to participate to the DeeFuzzer project!
We use GitHub to collaborate: https://github.com/yomguy/DeeFuzzer

Clone it, star it, join us!


Authors
=======

 * @yomguy +GuillaumePellerin yomguy@parisson.com
 * @achbed +achbed github@achbed.org
 * @choiz


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

GitHub: https://github.com/yomguy/DeeFuzzer

Expertise, Business, Sponsoring: http://parisson.com
