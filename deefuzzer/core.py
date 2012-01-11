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
from threading import Thread
from deefuzzer.station import *
from deefuzzer.tools import *

class DeeFuzzer(Thread):
    """a DeeFuzzer diffuser"""

    def __init__(self, conf_file):
        Thread.__init__(self)
        self.conf_file = conf_file
        self.conf = self.get_conf_dict()
        if 'log' in self.conf['deefuzzer'].keys():
            self.logger = Logger(self.conf['deefuzzer']['log'])
        else:
            self.logger = Logger('.' + os.sep + 'deefuzzer.log')
        if 'm3u' in self.conf['deefuzzer'].keys():
            self.m3u = self.conf['deefuzzer']['m3u']
        else:
            self.m3u = '.' + os.sep + 'deefuzzer.m3u'

        if isinstance(self.conf['deefuzzer']['station'], dict):
            # Fix wrong type data from xmltodict when one station (*)
            self.nb_stations = 1
        else:
            self.nb_stations = len(self.conf['deefuzzer']['station'])

        # Set the deefuzzer logger
        self.logger.write_info('Starting DeeFuzzer')
        self.logger.write_info('Using libshout version %s' % shout.version())

        # Init all Stations
        self.stations = []
        self.logger.write_info('Number of stations : ' + str(self.nb_stations))

    def get_conf_dict(self):
        confile = open(self.conf_file,'r')
        conf_xml = confile.read()
        confile.close()
        return xmltodict(conf_xml,'utf-8')

    def set_m3u_playlist(self):
        m3u_dir = os.sep.join(self.m3u.split(os.sep)[:-1])
        if not os.path.exists(m3u_dir):
            os.makedirs(m3u_dir)
        m3u = open(self.m3u, 'w')
        m3u.write('#EXTM3U\n')
        for s in self.stations:
            info = '#EXTINF:%s,%s - %s\n' % ('-1',s.short_name, s.channel.name)
            url =  'http://' + s.channel.host + ':' + str(s.channel.port) + s.channel.mount + '\n'
            m3u.write(info)
            m3u.write(url)
        m3u.close()
        self.logger.write_info('Writing M3U file to : ' + self.m3u)


    def run(self):
        q = Queue.Queue(1)

        for i in range(0,self.nb_stations):
            if isinstance(self.conf['deefuzzer']['station'], dict):
                station = self.conf['deefuzzer']['station']
            else:
                station = self.conf['deefuzzer']['station'][i]
            self.stations.append(Station(station, q, self.logger, self.m3u))

        self.set_m3u_playlist()
        p = Producer(q)
        p.start()

        # Start the Stations
        for i in range(0,self.nb_stations):
            self.stations[i].start()


class Producer(Thread):
    """a DeeFuzzer Producer master thread"""

    def __init__(self, q):
        Thread.__init__(self)
        self.q = q

    def run(self):
        i=0
        q = self.q
        while True:
            q.put(i,1)
            i+=1

