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
    
    def __init__(self, conf_file):
        self.conf_file = conf_file
        self.work_dir = os.environ['HOME']+'.d-fuzz'
        self.conf = []
        
        
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
        conf = open(self.conf_file,'r')
        conf_xml = conf.readlines()
        self.conf = xmltodict(conf_xml)

    def get_station_names(self):
        return self.conf['station']['name']
        
        

    def check_work_dir(self):
        if not os.isdir.exists(self.work_dir):
            os.mkdir(self.work_dir)

    def get_playlist(self):
        file_list = []
        for root, dirs, files in os.walk(self.media_dir):
            for file in files:
                file_list.append(root + os.sep + file)
        return file_list
                    


    for i in range(1,nb_ch+1):
        ch_name_i = radio_name+'_'+type+'_'+str(i)
        ch_ice_name_i = radio_name+'_'+str(i)
        ch_pre_i = work_dir+os.sep+ch_name_i
        fi_xml = open(ch_pre_i+'.xml','w')
        fi_xml.write('<ezstream>\n')
       
fi_xml.write('<url>http://'+server+':'+port+'/'+ch_ice_name_i+'.'+type+'</url>\
n')
        fi_xml.write('<format>'+string.upper(type)+'</format>\n')
            fi_xml.write('<filetype>script</filetype>\n')
            fi_xml.write('<filename>'+ch_pre_i+'.py</filename>\n')
        for line in l_descr:
            fi_xml.write(line)
        fi_xml.write('</ezstream>')
        fi_xml.close()
        fi_py = open(ch_pre_i+'.py','w')
        fi_py.write('#!/usr/bin/python\n\n')
        fi_py.write('import sys, os, random\n\n')
        fi_py.write('Playdir="'+audio_dir+os.sep+'"\n')
        fi_py.write('IndexFile="'+ch_pre_i+'_index.txt"\n')
       
fi_py.write('RandomIndexListFile="'+ch_pre_i+'_random_index_list.txt"\n')
       
fi_py.write('PlaylistLengthOrigFile="'+ch_pre_i+'_playlist_length.txt"\n\n')
        for line in l_tools:
            fi_py.write(line)
        fi_py.close()
        os.chmod(work_dir+os.sep+ch_name_i+'.py',0755)

    def stream(self, media_dir):
        """Looped stream of the media_dir"""


    for station in conf_dict['station']:

        s = shout.Shout()
        print "Using libshout version %s" % shout.version()

        s.host = self.server['host']
        s.port = self.server['port']
        s.user = 'source'
        s.password = self.conf['sourcepassword']
        s.mount = self.mountpoint
        s.format = self.conf['format']
        s.protocol = 'http'
        # | 'xaudiocast' | 'icy'
        s.name = self.conf['name']
        s.genre = self.conf['genre']
        # s.url = ''
        # s.public = 0 | 1
        # s.audio_info = { 'key': 'val', ... }
        #  (keys are shout.SHOUT_AI_BITRATE, shout.SHOUT_AI_SAMPLERATE,
        #   shout.SHOUT_AI_CHANNELS, shout.SHOUT_AI_QUALITY)

        s.open()

        total = 0
        st = time.time()
        for fa in sys.argv[1:]:
            print "opening file %s" % fa
            f = open(fa)
            s.set_metadata({'song': fa})

            nbuf = f.read(4096)
            while 1:
                buf = nbuf
                nbuf = f.read(4096)
                total = total + len(buf)
                if len(buf) == 0:
                    break
                s.send(buf)
                s.sync()
            f.close()
            
            et = time.time()
            br = total*0.008/(et-st)
            print "Sent %d bytes in %d seconds (%f kbps)" % (total, et-st, br)

        print s.close()
        
        #os.system('d-fuzz_loop '+ch_pre_i+' &')
        print ch_pre_i+' started !'
        


class Stream:

    def __init__(self):
        self.buffer_size = 0xFFFF
        
    def process:
        
        if len(sys.argv) == 2:
            station = DFuzz(sys.argv[1])
        sys.exit('')


        # Processing (streaming + cache writing)
        stream = self.core_process(self.command,self.buffer_size,self.dest)
        for chunk in stream:
            yield chunk
