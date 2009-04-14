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
from threading import Thread
from tools import *

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


class DeeFuzz(Thread):
    """a DeeFuzz diffuser"""

    def __init__(self, conf_file):
        Thread.__init__(self)
        self.conf_file = conf_file
        self.conf = self.get_conf_dict()

    def get_conf_dict(self):
        confile = open(self.conf_file,'r')
        conf_xml = confile.read()
        confile.close()
        dict = xmltodict(conf_xml,'utf-8')
        return dict

    def run(self):
        if isinstance(self.conf['deefuzz']['station'], dict):
            # Fix wrong type data from xmltodict when one station (*)
            nb_stations = 1
        else:
            nb_stations = len(self.conf['deefuzz']['station'])

        # Create a Queue
        # Not too much, otherwise, you will get memory leaks !
        q = Queue.Queue(1)

        # Create a Producer 
        p = Producer(q)
        p.start()

        # Set the deefuzz logger
        if 'log' in self.conf['deefuzz'].keys():
            self.logger = Logger(self.conf['deefuzz']['log'])
        else:
            self.logger = Logger('.' + os.sep + 'deefuzz.log')
            
        self.logger.write('Starting DeeFuzz v' + version)
        self.logger.write('Using libshout version %s' % shout.version())

        # Define the buffer_size
        self.buffer_size = 32768
        self.logger.write('Buffer size per station = ' + str(self.buffer_size))

        # Start the Stations
        s = []
        self.logger.write('Number of stations : ' + str(nb_stations))
        for i in range(0,nb_stations):
            if isinstance(self.conf['deefuzz']['station'], dict):
                station = self.conf['deefuzz']['station']
            else:
                station = self.conf['deefuzz']['station'][i]

            # Create a Station
            s.append(Station(station, q, self.buffer_size, self.logger))

        for i in range(0,nb_stations):
            s[i].start()   


class Producer(Thread):
    """a DeeFuzz Producer master thread"""

    def __init__(self, q):
        Thread.__init__(self)
        self.q = q

    def run(self):
        i=0
        q = self.q
        while 1: 
            q.put(i,1)
            i+=1


class Station(Thread):
    """a DeeFuzz shouting station thread"""

    def __init__(self, station, q, buffer_size, logger):
        Thread.__init__(self)
        self.station = station
        self.q = q
        self.buffer_size = buffer_size
        self.logger = logger
        self.channel = shout.Shout()
        self.id = 999999
        self.counter = 0
        self.index_list = []
        self.command = 'cat '
        # Media
        self.media_dir = self.station['media']['dir']
        self.channel.format = self.station['media']['format']
        self.mode_shuffle = int(self.station['media']['shuffle'])
        self.bitrate = self.station['media']['bitrate']
        self.ogg_quality = self.station['media']['ogg_quality']
        self.samplerate = self.station['media']['samplerate']
        self.voices = self.station['media']['voices']
        self.rss_dir = self.station['media']['rss_dir']
        self.rss_enclosure = self.station['media']['rss_enclosure']
        # Infos
        self.short_name = self.station['infos']['short_name']
        self.channel.name = self.station['infos']['name']
        self.channel.genre = self.station['infos']['genre']
        self.channel.description = self.station['infos']['description']
        self.channel.url = self.station['infos']['url']
        
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
        self.set_playlist()
        self.lp = len(self.playlist)
        self.channel.open()

        # Logging
        self.logger.write('Opening ' + self.short_name + ' - ' + self.channel.name + \
                ' (' + str(self.lp) + ' tracks)...')

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

            if self.rss_enclosure == '1':
                rss_item_list.append(PyRSS2Gen.RSSItem(
                    title = media.metadata['artist'] + ' : ' + media.metadata['title'],
                    link = media_link,
                    description = media_description,
                    enclosure = PyRSS2Gen.Enclosure(media_link, str(media.size), 'audio/mpeg'),
                    guid = PyRSS2Gen.Guid(media_link),
                    pubDate = media_date,)
                    )
            else:
                rss_item_list.append(PyRSS2Gen.RSSItem(
                    title = media.metadata['artist'] + ' : ' + media.metadata['title'],
                    link = media_link,
                    description = media_description,
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

    def set_playlist(self):
        file_list = []
        for root, dirs, files in os.walk(self.media_dir):
            for file in files:
                s = file.split('.')
                ext = s[len(s)-1]
                if ext.lower() == self.channel.format and not '/.' in file:
                    file_list.append(root + os.sep + file)
        self.playlist = file_list

    def get_next_media(self):
        # Init playlist
        if self.lp != 0:
            self.set_playlist()
            lp_new = len(self.playlist)

            if lp_new != self.lp or self.counter == 0:
                self.id = 0
                self.lp = lp_new
                self.index_list = range(0,self.lp)
                if self.mode_shuffle == 1:
                    # Shake it, Fuzz it !
                    random.shuffle(self.index_list)
                self.logger.write('Station ' + self.short_name + \
                                 ' : generating new playlist (' + str(self.lp) + ' tracks)')
                self.update_rss(self.media_to_objs(self.playlist), self.rss_playlist_file)
            # Or follow...
            else:
                self.id = (self.id + 1) % self.lp

            return self.playlist[self.index_list[self.id]]

    def log_queue(self, it):
        print 'Station ' + self.short_name + ' eated one queue step: '+str(it)

    def media_to_objs(self, media_list):
        media_objs = []
        for media in media_list:
            file_name, file_title, file_ext = self.get_file_info(media)
            if file_ext.lower() == 'mp3':
                media_objs.append(Mp3(media))
            elif file_ext.lower() == 'ogg':
                media_objs.append(Ogg(media))
        return media_objs

    def get_file_info(self, media):
        file_name = media.split(os.sep)[-1]
        file_title = file_name.split('.')[:-2]
        try:
            file_title = file_title[0]
        except:
            pass
        file_ext = file_name.split('.')[-1]
        return file_name, file_title, file_ext
            
    def core_process_stream(self, media):
        """Read media and stream data through a generator.
        Taken from Telemeta (see http://telemeta.org)"""

        command = self.command + '"' + media + '"'

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
            if not __chunk:
                break
            yield __chunk

    def core_process_read(self, media):
        """Read media and stream data through a generator.
        Taken from Telemeta (see http://telemeta.org)"""

        m = open(media, 'r')
        while True:
            __chunk = m.read(self.buffer_size)
            if not __chunk:
                break
            yield __chunk
        m.close()

    def run(self):
        q = self.q
        while True:
            it = q.get(1)
            if self.lp == 0:
                self.logger.write('Error : Station ' + self.short_name + ' have no media to stream !')
                break
            media = self.get_next_media()
            self.counter += 1
            q.task_done()
   
            if os.path.exists(media) and not os.sep+'.' in media:
                it = q.get(1)
                file_name, file_title, file_ext = self.get_file_info(media)
                try:
                    self.current_media_obj = self.media_to_objs([media])
                except:
                    self.logger.write('Error : Station ' + self.short_name + ' : ' + media + 'not found !')
                    break
                title = self.current_media_obj[0].metadata['title']
                artist = self.current_media_obj[0].metadata['artist']
                if not (title or artist):
                    song = str(file_title)
                else:
                    song = str(artist) + ' : ' + str(title)
                self.channel.set_metadata({'song': song})
                self.update_rss(self.current_media_obj, self.rss_current_file)
                self.logger.write('DeeFuzzing this file on %s :  id = %s, index = %s, name = %s' \
                                    % (self.short_name, self.id, self.index_list[self.id], file_name))
                stream = self.core_process_stream(media)
                q.task_done()
                
                for __chunk in stream:
                    it = q.get(1)
                    self.channel.send(__chunk)
                    self.channel.sync()
                    q.task_done()
                #stream.close()
                
        self.channel.close()


def main():
    if len(sys.argv) == 2:
        d = DeeFuzz(sys.argv[1])
        d.start()
    else:
        text = prog_info()
        sys.exit(text)

if __name__ == '__main__':
    main()
