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
from tools import *
from xmltodict import xmltodict
from mutagen.oggvorbis import OggVorbis


class DFuzz:
    """A d-fuzz station"""
    
    def __init__(self):
        
        self.work_dir = os.environ['HOME']+'.d-fuzz'
        self.conf = []
        self.id = 0
        self.buffer_size = 0xFFFF
        
        
    def prog_info(self):
        return """
        d-fuzz : easy and light streaming tool

        Copyright (c) 2007-2007 Guillaume Pellerin <pellerin@parisson.com>
        All rights reserved.
        
        This software is licensed as described in the file COPYING, which
        you should have received as part of this distribution. The terms
        are also available at http://svn.parisson.org/d-fuzz/DFuzzLicense.2
        
        depends : ezstream (patched), icecast2, python,
        
        Usage : d-fuzz $1
            where $1 is the path for a config file
            ex: d-fuzz /etc/d-fuzz/myfuzz.conf

        see http://parisson.com/d-fuzz/ for more details
        """

    def get_conf_dict(self):
        confile = open(self.conf_file,'r')
        conf_xml = confile.readlines()
        self.conf = xmltodict(conf_xml)
        confile.close()

    def get_station_names(self):
        return self.conf['station']['name']
        
        

    def check_work_dir(self):
        if not os.isdir.exists(self.work_dir):
            os.mkdir(self.work_dir)
    
    def get_playlist_length(self):
        pass
        

    def get_playlist(self):
        file_list = []
        for root, dirs, files in os.walk(self.media_dir):
            for file in files:
                file_list.append(root + os.sep + file)
        return file_list

    def get_next_media(self):
        playlist = self.get_playlist()
        lp = len(playlist)
        if self.id > lp:
            self.id = 0
        else:
            self.id = self.id + 1
        yield playlist[self.id]
    
    

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
            raise ExportProcessError('Command failure:', command, proc)
            

        # Core processing
        while True:
            __chunk = proc.stdout.read(buffer_size)
            status = proc.poll()
            if status != None and status != 0:
                raise ExportProcessError('Command failure:', command, proc)
            if len(__chunk) == 0:
                break
            yield __chunk
            #file_out.write(__chunk)

        #file_out.close()

    def stream(self, conf_file): 
        self.conf_file = conf_file
        self.get_conf_dict()
#       for station in conf_dict['station']:
        chi = 0
        station = self.conf['station']
        
        s = shout.Shout()
        print "Using libshout version %s" % shout.version()
        
        self.media_dir = station['media']['media_dir'][chi]
        
        s.host = station['server']['host'][chi]
        s.port = station['server']['port'][chi]
        s.user = 'source'
        s.password = station['server']['sourcepassword'][chi]
        s.mount = station['server']['mountpoint'][chi]
        s.format = station['media']['format'][chi]
        s.protocol = 'http'
        # | 'xaudiocast' | 'icy'
        s.name = station['infos']['name']
        s.genre = station['infos']['genre']
        # s.url = ''
        # s.public = 0 | 1
        # s.audio_info = { 'key': 'val', ... }
        #  (keys are shout.SHOUT_AI_BITRATE, shout.SHOUT_AI_SAMPLERATE,
        #   shout.SHOUT_AI_CHANNELS, shout.SHOUT_AI_QUALITY)
        
        

        s.open()

        total = 0
        st = time.time()
        command = 'cat '
        
        for media in self.get_next_media():
            print "opening file %s" % media
            command = 'cat '+media_dir
            stream = self.core_process(command, self.buffer_size)
            #s.set_metadata({'song': fa})
            
            for chunk in stream:
                total = total + len(self.buffer_size)
                s.send(chunk)
                s.sync()
                        
            et = time.time()
            br = total*0.008/(et-st)
            print "Sent %d bytes in %d seconds (%f kbps)" % (total, et-st, br)

        print s.close()
        
        

if len(sys.argv) == 2:
    station = DFuzz()
    station.stream(sys.argv[1])
else:
    sys.exit('No way :(')


