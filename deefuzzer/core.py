#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2006-2011 Guillaume Pellerin

# <yomguy@parisson.com>

# This software is a computer program whose purpose is to stream audio
# and video data through icecast2 servers.

# This software is governed by the CeCILL license under French law and
# abiding by the rules of distribution of free software. You can use,
# modify and/ or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# "http://www.cecill.info".

# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty and the software's author, the holder of the
# economic rights, and the successive licensors have only limited
# liability.

# In this respect, the user's attention is drawn to the risks associated
# with loading, using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean that it is complicated to manipulate, and that also
# therefore means that it is reserved for developers and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or
# data to be ensured and, more generally, to use and operate it in the
# same conditions as regards security.

# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.

# Author: Guillaume Pellerin <yomguy@parisson.com>

import os
import shout
import Queue
import datetime
import mimetypes
import hashlib
from threading import Thread
from deefuzzer.station import *
from deefuzzer.tools import *

mimetypes.add_type('application/x-yaml', '.yaml')


class DeeFuzzer(Thread):
    """a DeeFuzzer diffuser"""

    logger = None
    m3u = None
    rss = None
    station_settings = []
    station_instances = {}
    watchfolder = {}
    logqueue = Queue.Queue()
    mainLoop = False
    ignoreErrors = False
    maxretry = 0

    def __init__(self, conf_file):
        Thread.__init__(self)
        self.conf_file = conf_file
        self.conf = get_conf_dict(self.conf_file)

        if 'deefuzzer' not in self.conf:
            return

        # Get the log setting first (if possible)
        log_file = str(self.conf['deefuzzer'].pop('log', ''))
        self.log_dir = os.sep.join(log_file.split(os.sep)[:-1])
        if not os.path.exists(self.log_dir) and self.log_dir:
            os.makedirs(self.log_dir)
        self.logger = QueueLogger(log_file, self.logqueue)
        self.logger.start()

        for key in self.conf['deefuzzer'].keys():
            if key == 'm3u':
                self.m3u = str(self.conf['deefuzzer'][key])

            elif key == 'ignoreerrors':
                # Ignore errors and continue as long as possible
                self.ignoreErrors = bool(self.conf['deefuzzer'][key])

            elif key == 'maxretry':
                # Maximum number of attempts to restart the stations on crash.
                self.maxretry = int(self.conf['deefuzzer'][key])

            elif key == 'station':
                # Load station definitions from the main config file
                if not isinstance(self.conf['deefuzzer'][key], list):
                    self.add_station(self.conf['deefuzzer'][key])
                else:
                    for s in self.conf['deefuzzer'][key]:
                        self.add_station(s)

            elif key == 'stationconfig':
                # Load additional station definitions from the requested folder
                self.load_stations_fromconfig(self.conf['deefuzzer'][key])

            elif key == 'stationfolder':
                # Create stations automagically from a folder structure
                if isinstance(self.conf['deefuzzer'][key], dict):
                    self.watchfolder = self.conf['deefuzzer'][key]
            else:
                setattr(self, key, self.conf['deefuzzer'][key])

        # Set the deefuzzer logger
        self._info('Starting DeeFuzzer')
        self._info('Using libshout version %s' % shout.version())
        self._info('Number of stations : ' + str(len(self.station_settings)))

    def _log(self, level, msg):
        try:
            obj = {'msg': 'Core: ' + str(msg), 'level': level}
            self.logqueue.put(obj)
        except:
            pass

    def _info(self, msg):
        self._log('info', msg)

    def _err(self, msg):
        self._log('err', msg)

    def set_m3u_playlist(self):
        m3u_dir = os.sep.join(self.m3u.split(os.sep)[:-1])
        if not os.path.exists(m3u_dir) and m3u_dir:
            os.makedirs(m3u_dir)
        m3u = open(self.m3u, 'w')
        m3u.write('#EXTM3U\n')
        for k in self.station_instances.keys():
            s = self.station_instances[k]
            m3u.write('#EXTINF:%s,%s - %s\n' % ('-1', s.short_name, s.channel.name))
            m3u.write('http://' + s.channel.host + ':' + str(s.channel.port) + s.channel.mount + '\n')
        m3u.close()
        self._info('Writing M3U file to : ' + self.m3u)

    def create_stations_fromfolder(self):
        """Scan a folder for subfolders containing media, and make stations from them all."""

        options = self.watchfolder
        if 'folder' not in options:
            # We have no folder specified.  Bail.
            return

        if self.mainLoop:
            if 'livecreation' not in options:
                # We have no folder specified.  Bail.
                return

            if int(options['livecreation']) == 0:
                # Livecreation not specified.  Bail.
                return

        folder = str(options['folder'])
        if not os.path.isdir(folder):
            # The specified path is not a folder.  Bail.
            return

        # This makes the log file a lot more verbose.  Commented out since we report on new stations anyway.
        # self._info('Scanning folder ' + folder + ' for stations')

        if 'infos' not in options:
            options['infos'] = {}
        if 'short_name' not in options['infos']:
            options['infos']['short_name'] = '[name]'

        files = os.listdir(folder)
        for file in files:
            filepath = os.path.join(folder, file)
            if os.path.isdir(filepath):
                if folder_contains_music(filepath):
                    self.create_station(filepath, options)

    def station_exists(self, name):
        try:
            for s in self.station_settings:
                if 'infos' not in s:
                    continue
                if 'short_name' not in s['infos']:
                    continue
                if s['infos']['short_name'] == name:
                    return True
            return False
        except:
            pass
        return True

    def create_station(self, folder, options):
        """Create a station definition for a folder given the specified options."""

        s = {}
        path, name = os.path.split(folder)
        if self.station_exists(name):
            return
        self._info('Creating station for folder ' + folder)
        d = dict(path=folder, name=name)
        for i in options.keys():
            if 'folder' not in i:
                s[i] = replace_all(options[i], d)
        if 'media' not in s:
            s['media'] = {}
        s['media']['source'] = folder
        
        self.add_station(s)

    def load_stations_fromconfig(self, folder):
        """Load one or more configuration files looking for stations."""

        if isinstance(folder, dict) or isinstance(folder, list):
            # We were given a list or dictionary.  Loop though it and load em all
            for f in folder:
                self.load_station_configs(f)
            return

        if os.path.isfile(folder):
            # We have a file specified.  Load just that file.
            self.load_station_config(folder)
            return

        if not os.path.isdir(folder):
            # Whatever we have, it's not either a file or folder.  Bail.
            return

        self._info('Loading station config files in ' + folder)
        files = os.listdir(folder)
        for file in files:
            filepath = os.path.join(folder, file)
            if os.path.isfile(filepath):
                self.load_station_config(filepath)

    def load_station_config(self, file):
        """Load station configuration(s) from a config file."""

        self._info('Loading station config file ' + file)
        stationdef = get_conf_dict(file)
        if isinstance(stationdef, dict):
            if 'station' in stationdef:
                if isinstance(stationdef['station'], dict):
                    self.add_station(stationdef['station'])
                elif isinstance(stationdef['station'], list):
                    for s in stationdef['station']:
                        self.add_station(s)

    def add_station(self, this_station):
        """Adds a station configuration to the list of stations."""
        try:
            # We should probably test to see if we're putting the same station in multiple times
            # Same in this case probably means the same media folder, server, and mountpoint
            self.station_settings.append(this_station)
        except Exception:
            return

    def run(self):
        q = Queue.Queue(1)
        ns = 0
        p = Producer(q)
        p.start()
        # Keep the Stations running
        while True:
            self.create_stations_fromfolder()
            ns_new = len(self.station_settings)
            if ns_new > ns:
                self._info('Loading new stations')
            
            for i in range(0, ns_new):
                name = ''
                try:
                    if 'station_name' in self.station_settings[i]:
                        name = self.station_settings[i]['station_name']
                    
                    if 'retries' not in self.station_settings[i]:
                        self.station_settings[i]['retries'] = 0
                        
                    try:
                        if 'station_instance' in self.station_settings[i]:
                            # Check for station running here
                            if self.station_settings[i]['station_instance'].isAlive():
                                # Station exists and is alive.  Don't recreate.
                                self.station_settings[i]['retries'] = 0
                                continue
                            
                            if self.maxretry >= 0 and self.station_settings[i]['retries'] <= self.maxretry:
                                # Station passed the max retries count is will not be reloaded
                                if 'station_stop_logged' not in self.station_settings[i]:
                                    self._err('Station ' + name + ' is stopped and will not be restarted.')
                                    self.station_settings[i]['station_stop_logged'] = True
                                continue

                            self.station_settings[i]['retries'] += 1
                            trynum = str(self.station_settings[i]['retries'])
                            self._info('Restarting station ' + name + ' (try ' + trynum + ')')
                    except Exception as e:
                        self._err('Error checking status for ' + name)
                        self._err(str(e))
                        if not self.ignoreErrors:
                            raise

                    # Apply station defaults if they exist
                    if 'stationdefaults' in self.conf['deefuzzer']:
                        if isinstance(self.conf['deefuzzer']['stationdefaults'], dict):
                            self.station_settings[i] = merge_defaults(
                                self.station_settings[i],
                                self.conf['deefuzzer']['stationdefaults']
                            )

                    if name == '':
                        name = 'Station ' + str(i)
                        if 'info' in self.station_settings[i]:
                            if 'short_name' in self.station_settings[i]['infos']:
                                name = self.station_settings[i]['infos']['short_name']
                                y = 1
                                while name in self.station_instances.keys():
                                    y += 1
                                    name = self.station_settings[i]['infos']['short_name'] + " " + str(y)

                        self.station_settings[i]['station_name'] = name
                        namehash = hashlib.md5(name).hexdigest()
                        self.station_settings[i]['station_statusfile'] = os.sep.join([self.log_dir, namehash])

                    new_station = Station(self.station_settings[i], q, self.logqueue, self.m3u)
                    if new_station.valid:
                        self.station_settings[i]['station_instance'] = new_station
                        self.station_settings[i]['station_instance'].start()
                        self._info('Started station ' + name)
                    else:
                        self._err('Error validating station ' + name)
                except Exception:
                    self._err('Error initializing station ' + name)
                    if not self.ignoreErrors:
                        raise
                    continue

                if self.m3u:
                    self.set_m3u_playlist()
                    
            ns = ns_new
            self.mainLoop = True

            time.sleep(5)
            # end main loop


class Producer(Thread):
    """a DeeFuzzer Producer master thread.  Used for locking/blocking"""

    def __init__(self, q):
        Thread.__init__(self)
        self.q = q

    def run(self):
        while True:
            try:
                self.q.put(True, True)
            except:
                pass

