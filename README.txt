
Introduction
============

DeeFuzzer is a new light and instant software made for streaming audio and video over internet. 
It is dedicated to people who wants to create playlisted web radios or web TVs with rich media contents including some metadata.

Here are the main features of the deefuzzer:

 * MP3 and OGG (audio & video) file streaming over internet (Icecast)
 * Full metadata encapsulation and management
 * RSS podcast generator (current tracks and playlists)
 * M3U playlist generator
 * Recursive, random (shuffled) or pre-defined playlists
 * Multi-threaded architecture : multiple station streaming with one config file
 * Auto Twitter posting of the current playing and new tracks
 * Jingling between main tracks
 * OSC controller : control the main functions from a distant terminal
 * Station relaying : stream other stations like *LIVE* sessions !
 * Very light and optimized streaming process

It is neccessary to provide a config file which sets all needed parameters
Please see example/myfuzz.xml for an example.


Installation
============

see INSTALL


License
=======

This software is licensed as described in the file LICENSE, which
you should have received as part of this distribution. The terms
are also available at http://svn.parisson.org/deefuzzer/DeeFuzzerLicense


Usage
=====

Usage : deefuzzer CONFIGFILE

where CONFIGFILE is the path for a XML config file. For example::

    deefuzzer example/deefuzzer.xml

To make the deefuzzer act as a deamon, just play it in the background::

    deefuzzer example/deefuzzer.xml &

Note that you must edit the config file with right parameters before playing.
You can find an example for a draft XML file in the directory "example/" of this
application (maybe in /usr/share/deefuzzer/example/ if installed with the help of install.py)

Since 0.3, deefuzzer doesn't print anything into the shell, then a right <log> parameter
is needed in the XML config file.

BE CAREFULL : at the moment, the multi-threaded implementation of deefuzzer instances
avoids shutting down the streams with CTRL+C... You have to kill them manually,
after a CTRL+Z, making this::

    pkill -9 deefuzzer


XML Configuration
=================

See example/deefuzz_doc.xml in a text editor.
The inline comments should help you to configure your stations.


OSC Control
===========

We can now control some functions of the deefuzzer with external commands
coming from an OSC client. These are accessible only if the "control" tag is
set up in the config file (see example/deefuzzer.xml again...).

Next track::

    python deefuzzer/scripts/osc_next.py

Start twitting::

    python deefuzzer/scripts/osc_twitter_start.py

Stop twitting::

    python deefuzzer/scripts/osc_twitter_stop.py

Start relaying::

    python deefuzzer/scripts/osc_relay_start.py

Stop relaying::

    python deefuzzer/scripts/osc_relay_stop.py

Start jingling::

    python deefuzzer/scripts/osc_jingles_start.py

Stop jingling::

    python deefuzzer/scripts/osc_jingles_stop.py


Author
======

Guillaume Pellerin <yomguy@parisson.com>


License
=======

See COPYING


Aknowledgements
===============

This work is inspired by the great - C coded - Oddsock's streaming program : Ezstream.
Since I needed to patch it in order to modify the playlist (randomize for example)
and make external batch tools to create multiple channels, I decided to rewrite it
from scratch in python.

Some parts of this work are also taken from another Parisson's project : Telemeta
(see http://telemeta.org).


Contact / Infos
===============

see http://svn.parisson.org/deefuzzer/ or http://parisson.com for more info.

