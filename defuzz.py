#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2007-2009 Guillaume Pellerin <yomguy@parisson.com>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution. The terms
# are also available at http://svn.parisson.org/defuzz/wiki/DefuzzLicense.
#
# Author: Guillaume Pellerin <yomguy@parisson.com>

import os
import sys
import time
import datetime
import string
import random
import Queue
import shout
import subprocess
from tools import *
from threading import Thread
from mutagen.oggvorbis import OggVorbis

version = '0.2.2'
year = datetime.datetime.now().strftime("%Y")


def prog_info():
        desc = '\n defuzz : easy and light streaming tool\n'
        ver = ' version : %s \n\n' % (version)
        info = """ Copyright (c) 2007-%s Guillaume Pellerin <yomguy@parisson.com>
 All rights reserved.
        
 This software is licensed as described in the file COPYING, which
 you should have received as part of this distribution. The terms
 are also available at http://svn.parisson.org/d-fuzz/DeFuzzLicense
        
 depends : python, python-xml, python-shout, libshout3, icecast2
 recommends : python-mutagen
 provides : python-shout
       
 Usage : defuzz $1
  where $1 is the path for a XML config file
  ex: defuzz example/myfuzz.xml
 
 see http://svn.parisson.org/defuzz/ for more details
        """ % (year)
        text = desc + ver + info
        return text


class DeFuzzError:
    """The DeFuzz main error class"""
    def __init__(self, message, command, subprocess):
        self.message = message
        self.command = str(command)
        self.subprocess = subprocess

    def __str__(self):
        if self.subprocess.stderr != None:
            error = self.subprocess.stderr.read()
        else:
            error = ''
        return "%s ; command: %s; error: %s" % (self.message,
                                                self.command,
                                                error)

class DeFuzz:
    """A DeFuzz diffuser"""

    def __init__(self, conf_file):
        self.conf_file = conf_file
        self.conf = self.get_conf_dict()
        #print self.conf

    def get_conf_dict(self):
        confile = open(self.conf_file,'r')
        conf_xml = confile.read()
        confile.close()
        dict = xmltodict(conf_xml,'utf-8')
        return dict

    def get_station_names(self):
        return self.conf['station']['name']

    def start(self):
        # Fix wrong type data from xmltodict when one station (*)
        if isinstance(self.conf['defuzz']['station'], dict):
            nb_stations = 1
        else:
            nb_stations = len(self.conf['defuzz']['station'])
        print 'Number of stations : ' + str(nb_stations)

        # Create a Queue
        q = Queue.Queue(1)

        # Create a Producer 
        p = Producer(q)
        p.start()

        s = []
        for i in range(0,nb_stations):
            if isinstance(self.conf['defuzz']['station'], dict):
                station = self.conf['defuzz']['station']
            else:
                station = self.conf['defuzz']['station'][i]
            name = station['infos']['name']
            # Create a Station
            s.append(Station(station, q))

        for i in range(0,nb_stations):
            # Start the Stations
            s[i].start()
            time.sleep(0.1)
            pass


class Producer(Thread):
    """a DeFuzz Producer master thread"""

    def __init__(self, q):
        Thread.__init__(self)
        self.q = q

    def run(self):
        q = self.q
        i=0
        while 1 : 
            #print "Producer produced one queue step: "+str(i)
            self.q.put(i,1)
            i+=1


class Station(Thread):
    """a DeFuzz Station shouting slave thread"""

    def __init__(self, station, q):
        Thread.__init__(self)
        self.q = q
        self.station = station
        self.buffer_size = 4096
        self.channel = shout.Shout()
        self.id = 999999
        self.counter = 0
        self.rand_list = []
        self.command = 'cat '
        # Media
        self.media_dir = self.station['media']['dir']
        self.channel.format = self.station['media']['format']
        self.mode_shuffle = int(self.station['media']['shuffle'])
        self.bitrate = self.station['media']['bitrate']
        self.ogg_quality = self.station['media']['ogg_quality']
        self.samplerate = self.station['media']['samplerate']
        self.voices = self.station['media']['voices']
        # Infos
        self.short_name = self.station['infos']['short_name']
        self.channel.name = self.station['infos']['name']
        self.channel.genre = self.station['infos']['genre']
        self.channel.description = self.station['infos']['description']
        self.channel.url = self.station['infos']['url']
        self.rss_file = '/tmp/' + self.short_name + '.xml'
        # Server
        self.channel.protocol = 'http'     # | 'xaudiocast' | 'icy'
        self.channel.host = self.station['server']['host']
        self.channel.port = int(self.station['server']['port'])
        self.channel.user = 'source'
        self.channel.password = self.station['server']['sourcepassword']
        self.channel.mount = '/' + self.short_name + '.' + self.channel.format
        self.channel.public = int(self.station['server']['public'])
        self.channel.audio_info = { 'SHOUT_AI_BITRATE': self.bitrate,
                                    'SHOUT_AI_SAMPLERATE': self.samplerate,
                                    'SHOUT_AI_QUALITY': self.ogg_quality,
                                    'SHOUT_AI_CHANNELS': self.voices,
                                  }

        #time.sleep(0.1)

    def update_rss(self, file_name):
        self.media_url_dir = '/media/'
        rss = PyRSS2Gen.RSS2(
        title = self.channel.name,
        link = self.channel.url,
        description = self.channel.description,
        lastBuildDate = datetime.datetime.now(),

        items = [
        PyRSS2Gen.RSSItem(
            title = file_name,
            link = self.channel.url + self.media_url_dir + file_name,
            description = file_name,
            guid = PyRSS2Gen.Guid(self.channel.url + self.media_url_dir + file_name),
            pubDate = datetime.datetime(2003, 9, 6, 21, 31)),
        ])

        rss.write_xml(open(self.rss_file, "w"))

    def get_playlist(self):
        file_list = []
        for root, dirs, files in os.walk(self.media_dir):
            for file in files:
                if not '/.' in file:
                    file_list.append(root + os.sep + file)
        return file_list

    def get_next_media_lin(self, playlist):
        lp = len(playlist)
        if self.id >= (lp - 1):
            playlist = self.get_playlist()
            self.id = 0
        else:
            self.id = self.id + 1
        return playlist, playlist[self.id]

    def get_next_media_rand(self, playlist):
        lp = len(playlist)
        if self.id >= (lp - 1):
            playlist = self.get_playlist()
            lp_new = len(playlist)
            if lp_new != lp or self.counter == 0:
                self.rand_list = range(0,lp_new)
                random.shuffle(self.rand_list)
            self.id = 0
        else:
            self.id = self.id + 1
        index = self.rand_list[self.id]
        return playlist, playlist[index]


    def core_process(self, media, buffer_size):
        """Read media and stream data through a generator.
        Taken from Telemeta (see http://telemeta.org)"""

        command = self.command + '"' + media + '"'
        __chunk = 0
        try:
            proc = subprocess.Popen(command,
                    shell = True,
                    bufsize = buffer_size,
                    stdin = subprocess.PIPE,
                    stdout = subprocess.PIPE,
                    close_fds = True)
        except:
            raise DeFuzzError('Command failure:', command, proc)

        # Core processing
        while True:
            __chunk = proc.stdout.read(buffer_size)
            status = proc.poll()
            if status != None and status != 0:
                raise DeFuzzError('Command failure:', command, proc)
            if len(__chunk) == 0:
                break
            yield __chunk

    def run(self):
        #print "Using libshout version %s" % shout.version()
        q = self.q
        __chunk = 0
        self.channel.open()
        self.playlist = self.get_playlist()
        self.lp = len(self.playlist)
        self.rand_list = range(0,self.lp-1)
        print 'Opening ' + self.short_name + ' - ' + self.channel.name + \
                ' (' + str(self.lp) + ' tracks)...'

        while True:
            if self.lp == 0:
                break
            if self.mode_shuffle == 1:
                self.playlist, media = self.get_next_media_rand(self.playlist)
            else:
                self.playlist, media = self.get_next_media_lin(self.playlist)

            self.counter += 1
            if os.path.exists(media) and not '/.' in media:
                file_name = string.replace(media, self.media_dir + os.sep, '')
                self.channel.set_metadata({'song': file_name})
                self.update_rss(file_name)
                _stream = self.core_process(media, self.buffer_size)
                print 'Defuzzing this file on %s :  id = %s, name = %s' % (self.short_name, self.id, file_name)
                
                for __chunk in _stream:
                    if len(__chunk) == 0:
                        break
                    self.channel.send(__chunk)
                    self.channel.sync()
                    # Get the queue
                    it = q.get(1)
                    print "Station " + self.short_name + " eated 1 queue step: "+str(it)

        self.channel.close()


def main():
    if len(sys.argv) == 2:
        print "Defuzz v"+version
        defuzz_main = DeFuzz(sys.argv[1])
        defuzz_main.start()
    else:
        text = prog_info()
        sys.exit(text)

if __name__ == '__main__':
    main()

