#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2007-2007 Guillaume Pellerin <yomguy@parisson.com>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution. The terms
# are also available at http://svn.parisson.org/d-fuzz/wiki/DfuzzLicense.
#
# Author: Guillaume Pellerin <yomguy@parisson.com>

import os
import sys
import string
import random
import subprocess
import shout
from shout import Shout
from xmltodict import *
from threading import Thread
from mutagen.oggvorbis import OggVorbis


class DFuzz(Thread):
    """A D-Fuzz station"""
    
    def __init__(self, conf_file):
        Thread.__init__(self)
        self.status = -1
        self.version = '0.1'
        self.conf_file = conf_file

    def prog_info(self):
        desc = '\n d-fuzz : easy and light streaming tool\n'
        version = ' version : ' + self.version +'\n\n'
        info = """ Copyright (c) 2007-2007 Guillaume Pellerin <yomguy@parisson.com>
 All rights reserved.
        
 This software is licensed as described in the file COPYING, which
 you should have received as part of this distribution. The terms
 are also available at http://svn.parisson.org/d-fuzz/DFuzzLicense
        
 depends : python, python-xml, shout-python, libshout3, icecast2
 recommends : python-mutagen
 provides : shout-python
       
 Usage : d-fuzz $1
  where $1 is the path for a XML config file
  ex: d-fuzz /etc/d-fuzz/myfuzz.xml
 
 see http://parisson.com/d-fuzz/ for more details
        """
        text = desc + version + info
        return text

    def get_conf_dict(self):
        confile = open(self.conf_file,'r')
        conf_xml = confile.read()
        confile.close()
        return xmltodict(conf_xml,'utf-8')
        

    def get_station_names(self):
        return self.conf['station']['name']
        

    def run(self):
        print "D-fuzz v"+self.version
        self.conf = self.get_conf_dict()
        print self.conf
        nb_stations = len(self.conf['d-fuzz'])
        print str(nb_stations)
        
        for i in range(0,nb_stations):
            print str(i)
            station = self.conf['d-fuzz']['station']
            print station
            station_thread = Station(station)
            station_thread.start()


class Station(DFuzz):
    """A web station"""
    def __init__ (self, station):
        Thread.__init__(self)
        self.station = station
        print self.station
        self.channels = int(self.station['infos']['channels'])
        
    def run(self):
        for channel_id in range(0,self.channels):
            channel = Channel(self.station, channel_id)
            channel.start()
            


class Channel(Thread):
    """A channel shout thread"""

    def __init__(self, station, channel_id):
        Thread.__init__(self)
        self.channel_id = channel_id
        self.channel = shout.Shout()
        #self.station = station
        self.id = 999999
        self.rand_list = []
         # Media
        self.media_dir = station['media']['dir']

        self.channel.format = station['media']['format']
        self.mode_shuffle = int(station['media']['shuffle'])
        
        # Server
        self.channel.protocol = 'http'     # | 'xaudiocast' | 'icy'
        self.channel.host = station['server']['host']
        self.channel.port = int(station['server']['port'])
        self.channel.user = 'source'
        self.channel.password = station['server']['sourcepassword']
        self.channel.mount = '/' + station['infos']['short_name'] + '_' +  \
                                    str(self.id) + '.' + self.channel.format
        print self.channel.mount
        self.channel.public = int(station['server']['public'])

        # Infos
        self.channel.name = station['infos']['name']
        self.channel.genre = station['infos']['genre']
        self.channel.description = station['infos']['description']
        self.channel.url = station['infos']['url']
        # s.audio_info = { 'key': 'val', ... }
        #  (keys are shout.SHOUT_AI_BITRATE, shout.SHOUT_AI_SAMPLERATE,
        #   shout.SHOUT_AI_CHANNELS, shout.SHOUT_AI_QUALITY)

        # Playlist
        self.playlist = self.get_playlist()
        self.lp = len(self.playlist)
        self.rand_list = range(0,self.lp)
        random.shuffle(self.rand_list)


    def get_playlist(self):
        file_list = []
        for root, dirs, files in os.walk(self.media_dir):
            for file in files:
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
            if lp_new != lp:
                self.rand_list = range(0,lp_new)
                random.shuffle(self.rand_list)
            print self.rand_list
            self.id = 0
        else:
            self.id = self.id + 1
        index = self.rand_list[self.id]
        print str(self.id) +':'+ str(index)
        return playlist, playlist[index]


    def run(self):
        print "Using libshout version %s" % shout.version()
        print 'Playlist :'
        print self.playlist
      
        self.channel.open()
        while 1:
            if self.lp == 0:
                break
            if self.mode_shuffle == 1:
                self.playlist, media = self.get_next_media_rand(self.playlist)
            else:
                self.playlist, media = self.get_next_media_lin(self.playlist)
            print media
            file_name = string.replace(media, self.media_dir + os.sep, '')
            self.channel.set_metadata({'song': file_name})
            stream = Stream(self.media_dir, media)
            print 'D-fuzz file : %s' % file_name
            for chunk in stream.run():
                self.channel.send(chunk)
                self.channel.sync()
        self.channel.close()


class Stream:
    """Streaming class"""
    
    def __init__(self, media_dir, media):
        #Thread.__init__(self)
        self.media = media
        self.media_dir = media_dir
        self.command = 'cat'
        self.buffer_size = 0xFFFF
        
    def core_process(self, command, buffer_size):
        """Apply command and stream data through a generator. 
        Taken from Telemeta..."""
        
        __chunk = 0
        try:
            proc = subprocess.Popen(command,
                                    shell = True,
                                    bufsize = buffer_size,
                                    stdin = subprocess.PIPE,
                                    stdout = subprocess.PIPE,
                                    close_fds = True)
        except:
            raise IOError('Command failure:', command, proc)

        # Core processing
        while True:
            __chunk = proc.stdout.read(buffer_size)
            status = proc.poll()
            #if status != None and status != 0:
                #raise ExportProcessError('Command failure:', command, proc)
            if len(__chunk) == 0:
                break
            yield __chunk
            
    def run(self):
        command = self.command + ' "%s"' % self.media
        stream = self.core_process(command, self.buffer_size)
        for chunk in stream:
            yield chunk



class DFuzzError:

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

                                                
def main():    
    if len(sys.argv) == 2:
        dfuzz_main = DFuzz(sys.argv[1])
        dfuzz_main.run()
    else:
        sys.exit('NO WAY !')

if __name__ == '__main__':
    main()

