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
from threading import Thread
from deefuzzer.station import *
from deefuzzer.tools import *

mimetypes.add_type('application/x-yaml','.yaml')


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

    def __init__(self, conf_file):
        Thread.__init__(self)
        self.conf_file = conf_file
        self.conf = get_conf_dict(self.conf_file)

        if not 'deefuzzer' in self.conf.keys():
            return 

        # Get the log setting first (if possible)
        log_file = str(self.conf['deefuzzer'].pop('log', ''))
        log_dir = os.sep.join(log_file.split(os.sep)[:-1])
        if not os.path.exists(log_dir) and log_dir:
            os.makedirs(log_dir)
        self.logger = QueueLogger(log_file, self.logqueue)
        self.logger.start()

        for key in self.conf['deefuzzer'].keys():
            if key == 'm3u':
                self.m3u = str(self.conf['deefuzzer'][key])

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
            obj = {}
            obj['msg'] = 'Core: ' + str(msg)
            obj['level'] = level
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
            m3u.write('#EXTINF:%s,%s - %s\n' % ('-1',s.short_name, s.channel.name))
            m3u.write('http://' + s.channel.host + ':' + str(s.channel.port) + s.channel.mount + '\n')
        m3u.close()
        self._info('Writing M3U file to : ' + self.m3u)

    def create_stations_fromfolder(self):
        """Scan a folder for subfolders containing media, and make stations from them all."""

        options = self.watchfolder
        if not 'folder' in options.keys():
            # We have no folder specified.  Bail.
            return

        if self.mainLoop:
            if not 'livecreation' in options.keys():
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

        files = os.listdir(folder)
        for file in files:
            filepath = os.path.join(folder, file)
            if os.path.isdir(filepath):
                if folder_contains_music(filepath):
                    self.create_station(filepath, options)

    def station_exists(self, name):
        try:
            for s in self.station_settings:
                if not 'infos' in s.keys():
                    continue
                if not 'short_name' in s['infos'].keys():
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
        d = dict(path=folder,name=name)
        for i in options.keys():
            if not 'folder' in i:
                s[i] = replace_all(options[i], d)
        if not 'media' in s.keys():
            s['media'] = {}
        s['media']['dir'] = folder
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
            if 'station' in stationdef.keys():
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
            if(ns_new > ns):
                self._info('Loading new stations')
                for i in range(0, ns_new):
                    try:
                        station = self.station_settings[i]
                        if 'station_name' in station.keys():
                            continue

                        # Apply station defaults if they exist
                        if 'stationdefaults' in self.conf['deefuzzer']:
                            if isinstance(self.conf['deefuzzer']['stationdefaults'], dict):
                                station = merge_defaults(station, self.conf['deefuzzer']['stationdefaults'])

                        name = 'Station ' + str(i)
                        if 'info' in station.keys():
                            if 'short_name' in station['infos']:
                                name = station['infos']['short_name']
                                y = 1
                                while name in self.station_instances.keys():
                                    y = y + 1
                                    name = station['infos']['short_name'] + " " + str(y)

                        self.station_settings[i]['station_name'] = name
                        new_station = Station(station, q, self.logqueue, self.m3u)
                        if new_station.valid:
                            self.station_instances[name] = new_station
                            self.station_instances[name].start()
                            self._info('Started station ' + name)
                        else:
                            self._err('Error validating station ' + name)
                    except Exception:
                        self._err('Error starting station ' + name)
                        continue
                ns = ns_new

                if self.m3u:
                    self.set_m3u_playlist()
            
            for i in self.station_instances.keys():
                try:
                    if not self.station_instances[i].isAlive():
                        self.station_instances[i].start()
                        self._info('Restarted crashed station ' + i)
                except:
                    pass
            
            self.mainLoop = True
            time.sleep(5)
            # end main loop


class Producer(Thread):
    """a DeeFuzzer Producer master thread.  Used for locking/blocking"""

    def __init__(self, q):
        Thread.__init__(self)
        self.q = q

    def run(self):
        i=0
        q = self.q
        while True:
            q.put(i,1)
            i+=1
