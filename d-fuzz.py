#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2007-2007 Guillaume Pellerin <pellerin@parisson.com>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution. The terms
# are also available at http://svn.parisson.org/d-fuzz/DFuzzLicense.
#
# Author: Guillaume Pellerin <pellerin@parisson.com>

import os
import sys
import shout
import string
import subprocess
from tools import *
from xmltodict import xmltodict
from mutagen.oggvorbis import OggVorbis


class ExportProcessError:

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

class DFuzz:
    """A D-Fuzz station"""
    
    def __init__(self):
        
        self.work_dir = os.environ['HOME']+'.d-fuzz'
        self.conf = []
        self.id = 999999
        self.buffer_size = 0xFFFF
        
    def prog_info(self):
        return """
 d-fuzz : easy and light streaming tool

 Copyright (c) 2007-2007 Guillaume Pellerin <pellerin@parisson.com>
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

    def get_conf_dict(self):
        confile = open(self.conf_file,'r')
        conf_xml = confile.read()
        self.conf = xmltodict(conf_xml,'utf-8')
        confile.close()

    def get_station_names(self):
        return self.conf['station']['name']
        
    def get_playlist(self):
        file_list = []
        for root, dirs, files in os.walk(self.media_dir):
            for file in files:
                file_list.append(root + os.sep + file)
        return file_list

    def get_next_media(self, playlist):
        lp = len(playlist)
        if self.id >= (lp - 1) :
            playlist = self.get_playlist()
            self.id = 0
        else:
            self.id = self.id + 1
        #print self.id
        return playlist, playlist[self.id]
    
    def get_random_media(self, playlist):
        lp = len(playlist)
        if self.id > lp:
            self.id = 0
        else:
            rand = randrange(0,lp)
            self.id = self.id + 1
        print self.id
        return playlist[self.id]

    def core_process(self, command, buffer_size):
        """Apply command and stream data through a generator. 
        From Telemeta..."""
        
        __chunk = 0
        #file_out = open(dest,'w')

        try:
            proc = subprocess.Popen(command,
                    shell = True,
                    bufsize = buffer_size,
                    stdin = subprocess.PIPE,
                    stdout = subprocess.PIPE,
                    close_fds = True)
        except:
            raise IOError('Command failure:', command, proc)
            #pass
        
        # Core processing
        while True:
            __chunk = proc.stdout.read(buffer_size)
            status = proc.poll()
            #if status != None and status != 0:
                #raise ExportProcessError('Command failure:', command, proc)
            if len(__chunk) == 0:
                break
            yield __chunk
            #file_out.write(__chunk)

        #file_out.close()

    def stream(self, conf_file): 
        self.conf_file = conf_file
        self.get_conf_dict()

        #for station in conf_dict['station']:
        
        station = self.conf['station']
        print station
        
        s = shout.Shout()
        print "Using libshout version %s" % shout.version()

        # Media
        self.media_dir = station['media']['dir']
        format = station['media']['format']
        s.format = format

        # Server
        s.protocol = 'http'     # | 'xaudiocast' | 'icy'
        s.host = station['server']['host']
        s.port = int(station['server']['port'])
        s.user = 'source'
        s.password = station['server']['sourcepassword']
        s.mount = '/' + station['infos']['short_name'] + '.' + format
        s.public = int(station['server']['public'])

        # Infos
        s.name = station['infos']['name']
        s.genre = station['infos']['genre']
        s.description = station['infos']['description']
        s.url = station['infos']['url']
        
        # s.audio_info = { 'key': 'val', ... }
        #  (keys are shout.SHOUT_AI_BITRATE, shout.SHOUT_AI_SAMPLERATE,
        #   shout.SHOUT_AI_CHANNELS, shout.SHOUT_AI_QUALITY)
        
        command = 'cat '
        playlist = self.get_playlist()
        lp = len(playlist)
        print 'Playlist :'
        print playlist
                    
        s.open()
        while True:
            if lp == 0:
                break 
            playlist, media = self.get_next_media(playlist)
            print 'opening file : %s' % media
            file_name = string.replace(media, self.media_dir + os.sep, '')
            print 'streaming file : %s' % file_name
            s.set_metadata({'song': file_name})
            command = 'cat "%s"' % media
            stream = self.core_process(command, self.buffer_size)
            for chunk in stream:
                s.send(chunk)
                s.sync()
        s.close()


def main():    
    station = DFuzz()
    if len(sys.argv) == 2:
        station.stream(sys.argv[1])
    else:
        text = station.prog_info()
        sys.exit(text)

if __name__ == '__main__':
    main()

