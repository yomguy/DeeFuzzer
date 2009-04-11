#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright Guillaume Pellerin (2006-2009)

# <yomguy@parisson.com>

# This software is a computer program whose purpose is to stream audio
# and video data through icecast2 servers.

# This software is governed by the CeCILL  license under French law and
# abiding by the rules of distribution of free software.  You can  use, 
# modify and/ or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# "http://www.cecill.info". 

# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability. 

# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or 
# data to be ensured and,  more generally, to use and operate it in the 
# same conditions as regards security.

# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.

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

version = '0.3'
year = datetime.datetime.now().strftime("%Y")


def prog_info():
        desc = '\n deefuzz : easy and light streaming tool\n'
        ver = ' version : %s \n\n' % (version)
        info = """ Copyright (c) 2007-%s Guillaume Pellerin <yomguy@parisson.com>
 All rights reserved.
        
 This software is licensed as described in the file COPYING, which
 you should have received as part of this distribution. The terms
 are also available at http://svn.parisson.org/d-fuzz/DeeFuzzLicense
        
 depends : python, python-xml, python-shout, libshout3, icecast2
 recommends : python-mutagen
 provides : python-shout
       
 Usage : deefuzz $1
  where $1 is the path for a XML config file
  ex: deefuzz example/myfuzz.xml
 
 see http://svn.parisson.org/deefuzz/ for more details
        """ % (year)
        text = desc + ver + info
        return text


class DeeFuzzError:
    """The DeeFuzz main error class"""
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


class DeeFuzz:
    """A DeeFuzz diffuser"""

    def __init__(self, conf_file):
        self.conf_file = conf_file
        self.conf = self.get_conf_dict()

    def get_conf_dict(self):
        confile = open(self.conf_file,'r')
        conf_xml = confile.read()
        confile.close()
        dict = xmltodict(conf_xml,'utf-8')
        return dict

    def get_station_names(self):
        return self.conf['station']['name']

    def play(self):
        if isinstance(self.conf['deefuzz']['station'], dict):
            # Fix wrong type data from xmltodict when one station (*)
            nb_stations = 1
        else:
            nb_stations = len(self.conf['deefuzz']['station'])
        print 'Number of stations : ' + str(nb_stations)

        # Create a Queue
        q = Queue.Queue(1)

        # Create a Producer 
        p = Producer(q)
        p.start()

        self.buffer_size = 65536/nb_stations
        print 'Buffer size per station = ' + str(self.buffer_size)
        
        s = []
        for i in range(0,nb_stations):
            if isinstance(self.conf['deefuzz']['station'], dict):
                station = self.conf['deefuzz']['station']
            else:
                station = self.conf['deefuzz']['station'][i]
            name = station['infos']['name']
            # Create a Station
            s.append(Station(station, q, self.buffer_size))

        for i in range(0,nb_stations):
            # Start the Stations
            s[i].start()            


class Producer(Thread):
    """a DeeFuzz Producer master thread"""

    def __init__(self, q):
        Thread.__init__(self)
        self.q = q

    def run(self):
        i=0
        while 1: 
            #print "Producer produced one queue step: "+str(i)
            self.q.put(i,1)
            i+=1


class Station(Thread):
    """a DeeFuzz Station shouting slave thread"""

    def __init__(self, station, q, buffer_size):
        Thread.__init__(self)
        self.station = station
        self.q = q
        self.buffer_size = buffer_size
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
        self.rss_dir = os.sep + 'tmp' + os.sep + 'rss'
        self.rss_current_file = self.rss_dir + os.sep + self.short_name + '_current.xml'
        self.rss_playlist_file = self.rss_dir + os.sep + self.short_name + '_playlist.xml'
        self.media_url_dir = '/media/'
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
        self.playlist = self.get_playlist()
        #print self.playlist
        self.lp = len(self.playlist)
        self.channel.open()
        print 'Opening ' + self.short_name + ' - ' + self.channel.name + \
                ' (' + str(self.lp) + ' tracks)...'
        #time.sleep(0.1)

    def update_rss(self, media_list, rss_file):
        rss_item_list = []
        if not os.path.exists(self.rss_dir):
            os.makedirs(self.rss_dir)
        
        if len(media_list) == 1:
            sub_title = '(currently playing)'
        else:
            sub_title = '(playlist)'
            
        for media in media_list:
            media_link = self.channel.url + self.media_url_dir + media.file_name
            media_description = '<table>'
            for key in media.metadata.keys():
                if media.metadata[key] != '':
                    media_description += '<tr><td>%s:   </td><td><b>%s</b></td></tr>' % \
                                            (key.capitalize(), media.metadata[key])
            media_description += '</table>'
            media_stats = os.stat(media.media)
            media_date = time.localtime(media_stats[8])
            media_date = time.strftime("%a, %d %b %Y %H:%M:%S +0000", media_date)
            
            rss_item_list.append(PyRSS2Gen.RSSItem(
                title = media.metadata['artist'] + ' : ' + media.metadata['title'],
                link = media_link,
                description = media_description,
                enclosure = PyRSS2Gen.Enclosure(media_link, str(media.size), 'audio/mpeg'),
                guid = PyRSS2Gen.Guid(media_link),
                pubDate = media_date,)
                )
                
        rss = PyRSS2Gen.RSS2(title = self.channel.name + ' ' + sub_title,
                            link = self.channel.url,
                            description = self.channel.description,
                            lastBuildDate = datetime.datetime.now(),
                            items = rss_item_list,)
        
        f = open(rss_file, 'w')
        rss.write_xml(f)
        f.close()

    def get_playlist(self):
        file_list = []
        for root, dirs, files in os.walk(self.media_dir):
            for file in files:
                s = file.split('.')
                ext = s[len(s)-1]
                if ext.lower() == self.channel.format and not '/.' in file:
                    file_list.append(root + os.sep + file)
        return file_list

    def get_next_media_lin(self):
        self.lp = len(self.playlist)
        if self.id >= (self.lp - 1):
            self.playlist = self.get_playlist()
            self.id = 0
            self.lp = len(self.playlist)
            self.update_rss(self.playlist_to_objs(), self.rss_playlist_file)
        else:
            self.id = self.id + 1
        return self.playlist[self.id]

    def get_next_media_rand(self):
        self.lp = len(self.playlist)
        if self.id >= (self.lp - 1):
            self.playlist = self.get_playlist()
            lp_new = len(self.playlist)
            if lp_new != self.lp or self.counter == 0:
                self.rand_list = range(0,lp_new)
                random.shuffle(self.rand_list)
            self.id = 0
            self.lp = len(self.playlist)
            self.update_rss(self.playlist_to_objs(), self.rss_playlist_file)
        else:
            self.id = self.id + 1
        index = self.rand_list[self.id]
        return self.playlist[index]

    def log_queue(self, it):
        print 'Station ' + self.short_name + ' eated one queue step: '+str(it)

    def playlist_to_objs(self):
        media_objs = []
        for media in self.playlist:
            file_name, file_title, file_ext = self.get_file_info(media)
            if file_ext.lower() == 'mp3':
                media_objs.append(Mp3(media))
            elif file_ext.lower() == 'ogg':
                media_objs.append(Ogg(media))
        return media_objs

    def get_file_info(self, media):
        file_name = media.split(os.sep)[-1]
        file_title = file_name.split('.')[-2]
        file_ext = file_name.split('.')[-1]
        return file_name, file_title, file_ext
            
    def core_process_stream(self, media):
        """Read media and stream data through a generator.
        Taken from Telemeta (see http://telemeta.org)"""

        command = self.command + '"' + media + '"'
        __chunk = 0

        try:
            proc = subprocess.Popen(command,
                    shell = True,
                    bufsize = self.buffer_size,
                    stdin = subprocess.PIPE,
                    stdout = subprocess.PIPE,
                    close_fds = True)
        except:
            raise DeeFuzzError('Command failure:', command, proc)

        # Core processing
        while True:
            __chunk = proc.stdout.read(self.buffer_size)
            status = proc.poll()
            if status != None and status != 0:
                raise DeeFuzzError('Command failure:', command, proc)
            if len(__chunk) == 0:
                break
            yield __chunk
        
    def core_process_read(self, media):
        """Read media and stream data through a generator.
        Taken from Telemeta (see http://telemeta.org)"""

        m = open(media, 'r')
        # Core processing
        while True:
            _chunk = m.read(self.buffer_size)
            if len(_chunk) == 0:
                break
            yield _chunk
        m.close()


    def run(self):
        q = self.q
        while True:
            it = q.get(1)
            if self.lp == 0:
                break
            if self.mode_shuffle == 1:
                media = self.get_next_media_rand()
            else:
                media = self.get_next_media_lin()
            self.counter += 1
            self.lp = len(self.playlist)
            file_name, file_title, file_ext = self.get_file_info(media)
            if file_ext.lower() == 'mp3':
                media_obj = Mp3(media)
            elif file_ext.lower() == 'ogg':
                media_obj = Ogg(media)

            q.task_done()
            #self.log_queue(it)
            
            if os.path.exists(media) and not os.sep+'.' in media:
                it = q.get(1)
                title = media_obj.metadata['title']
                self.channel.set_metadata({'song': str(title)})
                self.update_rss([media_obj], self.rss_current_file)
                print 'DeeFuzzing this file on %s :  id = %s, name = %s' % (self.short_name, self.id, file_name)
                stream = self.core_process_read(media)
                q.task_done()
                #self.log_queue(it)
                
                for _chunk in stream:
                    it = q.get(1)
                    self.channel.send(_chunk)
                    self.channel.sync()
                    q.task_done()
                    #self.log_queue(it)

        self.channel.close()


def main():
    if len(sys.argv) == 2:
        print "DeeFuzz v"+version
        print "Using libshout version %s" % shout.version()
        d = DeeFuzz(sys.argv[1])
        d.play()
    else:
        text = prog_info()
        sys.exit(text)

if __name__ == '__main__':
    main()
