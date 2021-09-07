#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2006-2011 Guillaume Pellerin

# <yomguy@parisson.com>

# This file is part of deefuzzer

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.



import os
import shout
import queue
import datetime
import mimetypes
import hashlib
import platform
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
    watch_folder = {}
    log_queue = queue.Queue()
    main_loop = False
    ignore_errors = False
    max_retry = 0

    def __init__(self, conf_file):
        Thread.__init__(self)
        self.conf_file = conf_file
        self.conf = get_conf_dict(self.conf_file)
        
        # print(self.conf)
        
        if 'deefuzzer' not in self.conf :
            raise('This is not a standard deefuzzer config file')

        # Get the log setting first (if possible)
        log_file = str(self.conf['deefuzzer'].pop('log', ''))
        self.log_dir = os.sep.join(log_file.split(os.sep)[:-1])
        if not os.path.exists(self.log_dir) and self.log_dir:
            os.makedirs(self.log_dir)
        self.logger = QueueLogger(log_file, self.log_queue)
        self.logger.start()

        for key in list(self.conf['deefuzzer'].keys()):
            if key == 'm3u':
                self.m3u = str(self.conf['deefuzzer'][key])

            elif key == 'ignoreerrors':
                # Ignore errors and continue as long as possible
                self.ignore_errors = bool(self.conf['deefuzzer'][key])

            elif key == 'max_retry':
                # Maximum number of attempts to restart the stations on crash.
                self.max_retry = int(self.conf['deefuzzer'][key])

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
                    self.watch_folder = self.conf['deefuzzer'][key]
            else:
                setattr(self, key, self.conf['deefuzzer'][key])

        # Set the deefuzzer logger
        self._info('Starting DeeFuzzer')
        self._info('Using Python version %s' % platform.python_version())
        self._info('Using libshout version %s' % shout.version())
        self._info('Number of stations : ' + str(len(self.station_settings)))

    def _log(self, level, msg):
        try:
            obj = {'msg': 'Core: ' + str(msg), 'level': level}
            self.log_queue.put(obj)
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
        for station in self.station_settings:
            m3u.write('#EXTINF:%s,%s\n' % ('-1', station['infos']['name']))
            m3u.write('http://' + station['server']['host'] + ':' + \
                str(station['server']['port']) + '/' + station['server']['mountpoint'] + '\n')
        m3u.close()
        self._info('Writing M3U file to : ' + self.m3u)

    def create_stations_fromfolder(self):
        """Scan a folder for subfolders containing media, and make stations from them all."""

        options = self.watch_folder
        if 'folder' not in options:
            # We have no folder specified.  Bail.
            return

        if self.main_loop:
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
        for i in list(options.keys()):
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
        q = queue.Queue(1)
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
                            if self.station_settings[i]['station_instance'].is_alive:
                                # Station exists and is alive.  Don't recreate.
                                self.station_settings[i]['retries'] = 0
                                continue

                            if self.max_retry >= 0 and self.station_settings[i]['retries'] <= self.max_retry:
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
                        if not self.ignore_errors:
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
                                while name in list(self.station_instances.keys()):
                                    y += 1
                                    name = self.station_settings[i]['infos']['short_name'] + " " + str(y)

                        self.station_settings[i]['station_name'] = name
                        namehash = hashlib.md5(str(name).encode('utf-8')).hexdigest()
                        self.station_settings[i]['station_statusfile'] = os.sep.join([self.log_dir, namehash])

                    new_station = Station(self.station_settings[i], q, self.log_queue, self.m3u)
                    if new_station.valid:
                        self.station_settings[i]['station_instance'] = new_station
                        self.station_settings[i]['station_instance'].start()
                        self._info('Started station ' + name)
                    else:
                        self._err('Error validating station ' + name)
                except Exception:
                    self._err('Error initializing station ' + name)
                    if not self.ignore_errors:
                        raise
                    continue

                if self.m3u:
                    self.set_m3u_playlist()

            ns = ns_new
            self.main_loop = True

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
