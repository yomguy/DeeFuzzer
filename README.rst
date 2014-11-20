.. image:: https://github.com/yomguy/DeeFuzzer/raw/master/doc/img/logo_deefuzzer.png

Introduction
============

DeeFuzzer is an open, light and instant software made for streaming audio and video over Internet.
It is dedicated to media streaming communities who wants to create web radios, web televisions,
live multimedia relaying or even as a personal home radio, with rich media contents including track metadata.

Here are the main features of the deefuzzer:

 * MP3, OGG Vorbis file and live streaming over Internet
 * Full metadata encapsulation and management
 * RSS podcast generator (current tracks and playlists)
 * M3U playlist generator
 * Recursive, random (shuffled) or pre-defined playlists
 * Multi-threaded architecture: multiple station streaming with one config file
 * Auto Twitter posting of the current playing and new tracks
 * Jingling between main tracks
 * OSC controller: control the main functions from a distant terminal
 * Relaying: relay and stream *LIVE* sessions!
 * Very light and optimized streaming process
 * Fully written in Python
 * Works with Icecast2, ShoutCast, Stream-m
 * EXPERIMENTAL: WebM video streaming support

It is only neccessary to provide a config file which sets all needed parameters.
Please see example/deefuzzer.xml for an example.

Because our aim is to get DeeFuzzer as light as possible it is NOT capable of re-encoding or transcoding media files.

News
=====

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

0.6.4 is out!

 * Fix install bug again (add main script to install), sorry :(
 * Reduce streaming buffer length

0.6.3 Fix install bug!

 * Setup rewritten
 * Fix MANIFEST

0.6.2 has been released!

 * No new functions but bugfixes (including a serious one during install from pypi)
 * Definitely moved the project to `GitHub <https://github.com/yomguy/DeeFuzzer>`_
 * Update various README details
 * update API doc: http://files.parisson.com/doc/deefuzzer/

0.6.1 is out!

 * New HTTP steamer based on pycurl to handle streaming over stream-m servers (WebM streaming)
   see http://code.google.com/p/stream-m/
 * Live webm relaying works good, webm playlist reading NEED testing
 * New <station><server><type> parameter ('icecast or 'stream-m')


Installation
============

DeeFuzzer has now only been well tested on Linux, but should work on any other platform.
You would then need to install libshout3 and liblo libraries for it. On Windows,
an install inside Gygwin should work well.

To install it, say on Debian, do::

    sudo apt-get install python-pip python-dev libshout3-dev python-liblo python-mutagen \
                         python-pycurl liblo-dev libshout3-dev librtmp-dev \
                         python-yaml libcurl4-openssl-dev python-mutagen

Now, the easiest way to install the DeeFuzzer from a shell::

    sudo pip install deefuzzer

or::

    sudo easy_install deefuzzer

to upgrade::

    sudo pip install --upgrade deefuzzer

To install the DeeFuzzer from sources, download the last archive `there <http://pypi.python.org/pypi/DeeFuzzer>`_

Uncompress, go to the deefuzzer app directory and run install as root. For example::

    tar xzf DeeFuzzer-0.6.5.tar.gz
    cd DeeFuzzer-0.6.5
    sudo python setup.py install

Follow the related package list to install optional or recommended applications:

 * **depends**: python, python-dev, python-shout (from pypi.python.org) | shout-python, libshout3, libshout3-dev, python-mutagen, python-pycurl | pycurl
 * **optional**: python-twitter, python-liblo | pyliblo (>= 0.26), python-yaml
 * **recommends**: icecast2, python-setuptools, stream-m

For more informations, please see on `GitHub <https://github.com/yomguy/DeeFuzzer>`_ or twitt a message to @parisson_studio

Usage
=====

Usage: deefuzzer CONFIGFILE

where CONFIGFILE is the path for a XML or YAML config file. For example::

    deefuzzer example/deefuzzer.xml

or::

    deefuzzer example/deefuzzer.yaml

To make the deefuzzer act as a deamon, just play it in the background::

    deefuzzer example/deefuzzer.yaml &

Note that you must edit the config file with right parameters before playing.
You can find an example for a draft XML file in the "example" directory of the source code.

WARNING: because we need the DeeFuzer to be a very stable streaming process with multiple channel management,
the multi-threaded implementation of deefuzzer instances avoids shutting down the process with a CTRL+C.
You have to kill them manually, after a CTRL+Z, making this::

    pkill -9 deefuzzer

or, more specificially::

    pkill -9 -f "deefuzzer example/deefuzzer.yaml"


Configuration
==============

Some examples of markup configuration files:

 * `generic XML <https://github.com/yomguy/DeeFuzzer/blob/master/example/deefuzzer.xml>`_
 * `generic and documented XML <https://github.com/yomguy/DeeFuzzer/blob/master/example/deefuzzer_doc.xml>`_
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
================================

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
============

Everybody is welcome to participate to the DeeFuzzer project!
We use GitHub to collaborate: https://github.com/yomguy/DeeFuzzer

Join us!

Author
======

YomguY aka Guillaume Pellerin:

 * twitter   @yomguy @parisson_studio
 * g+        +Guillaume Pellerin
 * email     <yomguy@parisson.com>

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
