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
import sys
import time
import datetime
import string
import random
import shout
import urllib
import mimetypes
from threading import Thread
from tools import *


class Station(Thread):
    """a DeeFuzzer shouting station thread"""

    id = 999999
    counter = 0
    command = 'cat '
    delay = 0
    start_time = time.time()

    def __init__(self, station, q, logger, m3u):
        Thread.__init__(self)
        self.station = station
        self.q = q
        self.logger = logger
        self.m3u = m3u
        self.server_ping = False

        # Media
        self.media_dir = self.station['media']['dir']
        self.media_format = self.station['media']['format']
        self.shuffle_mode = int(self.station['media']['shuffle'])
        self.bitrate = self.station['media']['bitrate']
        self.ogg_quality = self.station['media']['ogg_quality']
        self.samplerate = self.station['media']['samplerate']
        self.voices = self.station['media']['voices']

        # Server
        self.short_name = self.station['infos']['short_name']

        if 'type' in self.station['server']:
            self.type = self.station['server']['type'] #  'icecast' | 'stream-m'

        if self.type == 'stream-m':
            self.mount = '/publish/' + self.short_name
        elif self.type == 'icecast':
            self.mount = '/' + self.short_name
        else:
            self.mount = '/' + self.short_name

        if 'stream-m' in self.type:
            self.channel = HTTPStreamer()
            self.channel.mount = self.mount
        else:
            self.channel = shout.Shout()
            self.channel.mount = self.mount + '.' + self.media_format

        self.channel.url = self.station['infos']['url']
        self.channel.name = self.station['infos']['name'] + ' : ' + self.channel.url
        self.channel.genre = self.station['infos']['genre']
        self.channel.description = self.station['infos']['description']
        self.channel.format = self.media_format
        self.channel.host = self.station['server']['host']
        self.channel.port = int(self.station['server']['port'])
        self.channel.user = 'source'
        self.channel.password = self.station['server']['sourcepassword']
        self.channel.public = int(self.station['server']['public'])
        self.channel.genre = self.station['infos']['genre']
        self.channel.description = self.station['infos']['description']
        self.channel.audio_info = { 'bitrate': self.bitrate,
                                    'samplerate': self.samplerate,
                                    'quality': self.ogg_quality,
                                    'channels': self.voices,}
        self.server_url = 'http://' + self.channel.host + ':' + str(self.channel.port)
        self.channel_url = self.server_url + self.channel.mount

        # RSS
        self.rss_dir = self.station['rss']['dir']
        self.rss_enclosure = self.station['rss']['enclosure']
        if 'media_url' in self.station['rss']:
            self.rss_media_url = self.station['rss']['media_url']
            if self.rss_media_url[-1] != '/':
                self.rss_media_url = self.rss_media_url + '/'
        else:
            self.rss_media_url = self.channel.url + '/media/'
        self.base_name = self.rss_dir + os.sep + self.short_name + '_' + self.channel.format
        self.rss_current_file = self.base_name + '_current.xml'
        self.rss_playlist_file = self.base_name + '_playlist.xml'

        # Playlist
        self.playlist = self.get_playlist()
        self.lp = len(self.playlist)

        # Logging
        self.logger.write_info('Opening ' + self.short_name + ' - ' + self.channel.name + \
                ' (' + str(self.lp) + ' tracks)...')

        self.metadata_relative_dir = 'metadata'
        self.metadata_url = self.channel.url + '/rss/' + self.metadata_relative_dir
        self.metadata_dir = self.rss_dir + os.sep + self.metadata_relative_dir
        if not os.path.exists(self.metadata_dir):
            os.makedirs(self.metadata_dir)

        # The station's player
        self.player = Player()
        self.player_mode = 0

        # Jingling between each media.
        # mode = 0 means Off, mode = 1 means On
        self.jingles_mode = 0
        if 'jingles' in self.station:
            self.jingles_mode =  int(self.station['jingles']['mode'])
            self.jingles_shuffle = self.station['jingles']['shuffle']
            self.jingles_dir = self.station['jingles']['dir']
            if self.jingles_mode == 1:
                self.jingles_callback('/jingles', [1])

        # Relaying
        # mode = 0 means Off, mode = 1 means On
        self.relay_mode = 0
        if 'relay' in self.station:
            self.relay_mode = int(self.station['relay']['mode'])
            self.relay_url = self.station['relay']['url']
            self.relay_author = self.station['relay']['author']
            if self.relay_mode == 1:
                self.relay_callback('/media/relay', [1])

        # Twitting
        # mode = 0 means Off, mode = 1 means On
        self.twitter_mode = 0
        if 'twitter' in self.station:
            self.twitter_mode = int(self.station['twitter']['mode'])
            self.twitter_key = self.station['twitter']['key']
            self.twitter_secret = self.station['twitter']['secret']
            self.twitter_tags = self.station['twitter']['tags'].split(' ')
            try:
                self.twitter_messages = self.station['twitter']['message']
                if isinstance(self.twitter_messages,  dict):
                    self.twitter_messages = list(self.twitter_messages)
            except:
                pass

            if self.twitter_mode == 1:
                self.twitter_callback('/twitter', [1])

        # Recording
        # mode = 0 means Off, mode = 1 means On
        self.record_mode = 0
        if 'record' in self.station:
            self.record_mode = int(self.station['record']['mode'])
            self.record_dir = self.station['record']['dir']
            if self.record_mode == 1:
                self.record_callback('/record', [1])

        # Running
        # mode = 0 means Off, mode = 1 means On
        self.run_mode = 1

        # OSCing
        self.osc_control_mode = 0
        # mode = 0 means Off, mode = 1 means On
        if 'control' in self.station:
            self.osc_control_mode = int(self.station['control']['mode'])
            self.osc_port = self.station['control']['port']
            if self.osc_control_mode == 1:
                self.osc_controller = OSCController(self.osc_port)
                self.osc_controller.start()
                # OSC paths and callbacks
                self.osc_controller.add_method('/media/next', 'i', self.media_next_callback)
                self.osc_controller.add_method('/media/relay', 'i', self.relay_callback)
                self.osc_controller.add_method('/twitter', 'i', self.twitter_callback)
                self.osc_controller.add_method('/jingles', 'i', self.jingles_callback)
                self.osc_controller.add_method('/record', 'i', self.record_callback)
                self.osc_controller.add_method('/player', 'i', self.player_callback)
                self.osc_controller.add_method('/run', 'i', self.run_callback)

    def run_callback(self, path, value):
        value = value[0]
        self.run_mode = value
        message = "Station " + self.channel_url + " : received OSC message '%s' with arguments '%d'" % (path, value)
        self.logger.write_info(message)

    def media_next_callback(self, path, value):
        value = value[0]
        self.next_media = value
        message = "Station " + self.channel_url + " : received OSC message '%s' with arguments '%d'" % (path, value)
        self.logger.write_info(message)

    def relay_callback(self, path, value):
        value = value[0]
        if value == 1:
            self.relay_mode = 1
            if self.type == 'icecast':
                self.player.start_relay(self.relay_url)
        elif value == 0:
            self.relay_mode = 0
            if self.type == 'icecast':
                self.player.stop_relay()
        self.id = 0
        self.next_media = 1
        message = "Station " + self.channel_url + " : received OSC message '%s' with arguments '%d'" % (path, value)
        self.logger.write_info(message)
        message = "Station " + self.channel_url + " : relaying : %s" % self.relay_url
        self.logger.write_info(message)

    def twitter_callback(self, path, value):
        value = value[0]
        import tinyurl
        self.twitter = Twitter(self.twitter_key, self.twitter_secret)
        self.twitter_mode = value
        message = "Station " + self.channel_url + " : received OSC message '%s' with arguments '%d'" % (path, value)
        self.m3u_tinyurl = tinyurl.create_one(self.channel.url + '/m3u/' + self.m3u.split(os.sep)[-1])
        self.rss_tinyurl = tinyurl.create_one(self.channel.url + '/rss/' + self.rss_playlist_file.split(os.sep)[-1])
        self.logger.write_info(message)

    def jingles_callback(self, path, value):
        value = value[0]
        if value == 1:
            self.jingles_list = self.get_jingles()
            self.jingles_length = len(self.jingles_list)
            self.jingle_id = 0
        self.jingles_mode = value
        message = "Station " + self.channel_url + " : received OSC message '%s' with arguments '%d'" % (path, value)
        self.logger.write_info(message)

    def record_callback(self, path, value):
        value = value[0]
        if value == 1:
            if not os.path.exists(self.record_dir):
                os.makedirs(self.record_dir)
            self.rec_file = self.short_name.replace('/', '_') + '-' + \
              datetime.datetime.now().strftime("%x-%X").replace('/', '_') + '.' + self.channel.format
            self.recorder = Recorder(self.record_dir)
            self.recorder.open(self.rec_file)
        elif value == 0 and not self.type == 'stream-m':
            self.recorder.close()
            date = datetime.datetime.now().strftime("%Y")
            if self.channel.format == 'mp3':
                media = Mp3(self.record_dir + os.sep + self.rec_file)
            if self.channel.format == 'ogg':
                media = Ogg(self.record_dir + os.sep + self.rec_file)
            media.metadata = {'artist': self.artist.encode('utf-8'),
                                'title': self.title.encode('utf-8'),
                                'album': self.short_name.encode('utf-8'),
                                'genre': self.channel.genre.encode('utf-8'),
                                'date' : date.encode('utf-8'),}
            media.write_tags()
        self.record_mode = value
        message = "Station " + self.channel_url + " : received OSC message '%s' with arguments '%d'" % (path, value)
        self.logger.write_info(message)

    def player_callback(self, path, value):
        value = value[0]
        self.player_mode = value
        message = "Station " + self.channel_url + " : received OSC message '%s' with arguments '%d'" % (path, value)
        self.logger.write_info(message)

    def get_playlist(self):
        file_list = []
        for root, dirs, files in os.walk(self.media_dir):
            for file in files:
                s = file.split('.')
                ext = s[len(s)-1]
                if ext.lower() == self.channel.format and not os.sep+'.' in file:
                    file_list.append(root + os.sep + file)
        file_list.sort()
        return file_list

    def get_jingles(self):
        file_list = []
        for root, dirs, files in os.walk(self.jingles_dir):
            for file in files:
                s = file.split('.')
                ext = s[len(s)-1]
                if ext.lower() == self.channel.format and not os.sep+'.' in file:
                    file_list.append(root + os.sep + file)
        file_list.sort()
        return file_list

    def get_next_media(self):
        # Init playlist
        if self.lp != 0:
            playlist = self.playlist
            new_playlist = self.get_playlist()
            lp_new = len(new_playlist)

            if lp_new != self.lp or self.counter == 0:
                self.id = 0
                self.lp = lp_new

                # Twitting new tracks
                new_playlist_set = set(new_playlist)
                playlist_set = set(playlist)
                new_tracks = new_playlist_set - playlist_set
                self.new_tracks = list(new_tracks.copy())

                if len(new_tracks) != 0:
                    new_tracks_objs = self.media_to_objs(self.new_tracks)
                    for media_obj in new_tracks_objs:
                        title = media_obj.metadata['title']
                        artist = media_obj.metadata['artist']
                        if not (title or artist):
                            song = str(media_obj.file_name)
                        else:
                            song = artist + ' : ' + title
                        song = song.encode('utf-8')
                        artist = artist.encode('utf-8')
                        if self.twitter_mode == 1:
                            artist_names = artist.split(' ')
                            artist_tags = ' #'.join(list(set(artist_names)-set(['&', '-'])))
                            message = '#NEWTRACK ! %s #%s on #%s RSS: ' % (song.replace('_', ' '), artist_tags, self.short_name)
                            message = message[:113] + self.rss_tinyurl
                            self.update_twitter(message)

                # Shake it, Fuzz it !
                if self.shuffle_mode == 1:
                    random.shuffle(playlist)

                # Play new tracks first
                for track in self.new_tracks:
                    playlist.insert(0, track)
                self.playlist = playlist

                self.logger.write_info('Station ' + self.channel_url + \
                                 ' : generating new playlist (' + str(self.lp) + ' tracks)')
                self.update_rss(self.media_to_objs(self.playlist), self.rss_playlist_file, '(playlist)')

            if self.jingles_mode == 1 and (self.counter % 2) == 0 and not self.jingles_length == 0:
                media = self.jingles_list[self.jingle_id]
                self.jingle_id = (self.jingle_id + 1) % self.jingles_length
            else:
                media = self.playlist[self.id]
                self.id = (self.id + 1) % self.lp
            return media
        else:
            mess = 'No media in media_dir !'
            self.logger.write_error(mess)
            sys.exit(mess)

    def media_to_objs(self, media_list):
        media_objs = []
        for media in media_list:
            file_name, file_title, file_ext = get_file_info(media)
            if file_ext.lower() == 'mp3' and mimetypes.guess_type(media)[0] == 'audio/mpeg':
                try:
                    media_objs.append(Mp3(media))
                except:
                    continue
            elif file_ext.lower() == 'ogg' and mimetypes.guess_type(media)[0] == 'audio/ogg':
                try:
                    media_objs.append(Ogg(media))
                except:
                    continue
        return media_objs

    def update_rss(self, media_list, rss_file, sub_title):
        rss_item_list = []
        if not os.path.exists(self.rss_dir):
            os.makedirs(self.rss_dir)
        channel_subtitle = self.channel.name + ' ' + sub_title
        _date_now = datetime.datetime.now()
        date_now = str(_date_now)
        media_absolute_playtime = _date_now

        for media in media_list:
            media_stats = os.stat(media.media)
            media_date = time.localtime(media_stats[8])
            media_date = time.strftime("%a, %d %b %Y %H:%M:%S +0200", media_date)
            media.metadata['Duration'] = str(media.length).split('.')[0]
            media.metadata['Bitrate'] = str(media.bitrate) + ' kbps'
            media.metadata['Next play'] = str(media_absolute_playtime).split('.')[0]

            media_description = '<table>'
            media_description_item = '<tr><td>%s:   </td><td><b>%s</b></td></tr>'
            for key in media.metadata.keys():
                if media.metadata[key] != '':
                    media_description += media_description_item % (key.capitalize(), media.metadata[key])
            media_description += '</table>'

            title = media.metadata['title']
            artist = media.metadata['artist']
            if not (title or artist):
                song = str(media.file_title)
            else:
                song = artist + ' : ' + title

            media_absolute_playtime += media.length

            if self.rss_enclosure == '1':
                media_link = self.rss_media_url + media.file_name
                media_link = media_link.decode('utf-8')
                rss_item_list.append(RSSItem(
                    title = song,
                    link = media_link,
                    description = media_description,
                    enclosure = Enclosure(media_link, str(media.size), 'audio/mpeg'),
                    guid = Guid(media_link),
                    pubDate = media_date,)
                    )
            else:
                media_link = self.metadata_url + '/' + media.file_name + '.xml'
                try:
                    media_link = media_link.decode('utf-8')
                except:
                    continue
                rss_item_list.append(RSSItem(
                    title = song,
                    link = media_link,
                    description = media_description,
                    guid = Guid(media_link),
                    pubDate = media_date,)
                    )

        rss = RSS2(title = channel_subtitle,
                            link = self.channel.url,
                            description = self.channel.description.decode('utf-8'),
                            lastBuildDate = date_now,
                            items = rss_item_list,)
        f = open(rss_file, 'w')
        rss.write_xml(f, 'utf-8')
        f.close()

    def update_twitter(self, message):
        try:
            self.twitter.post(message.decode('utf8'))
            self.logger.write_info('Twitting : "' + message + '"')
        except:
            self.logger.write_error('Twitting : "' + message + '"')
            pass

    def set_relay_mode(self):
        self.prefix = '#nowplaying (relaying #LIVE)'
        self.title = self.channel.description.encode('utf-8')
        self.artist = self.relay_author.encode('utf-8')
        self.title = self.title.replace('_', ' ')
        self.artist = self.artist.replace('_', ' ')
        self.song = self.artist + ' : ' + self.title
        if self.type == 'stream-m':
            relay = URLReader(self.relay_url)
            self.channel.set_callback(relay.read_callback)
            if self.record_mode:
             relay.set_recorder(self.recorder)
        else:
            self.stream = self.player.relay_read()

    def set_read_mode(self):
        self.prefix = '#nowplaying'
        self.current_media_obj = self.media_to_objs([self.media])
        self.title = self.current_media_obj[0].metadata['title']
        self.artist = self.current_media_obj[0].metadata['artist']
        self.title = self.title.replace('_', ' ')
        self.artist = self.artist.replace('_', ' ')
        if not (self.title or self.artist):
            song = str(self.current_media_obj[0].file_name)
        else:
            song = self.artist + ' : ' + self.title
        self.song = song.encode('utf-8')
        self.artist = self.artist.encode('utf-8')
        self.metadata_file = self.metadata_dir + os.sep + self.current_media_obj[0].file_name + '.xml'
        #self.update_rss(self.current_media_obj, self.metadata_file, '')
        self.update_rss(self.current_media_obj, self.rss_current_file, '(currently playing)')
        self.logger.write_info('DeeFuzzing on %s :  id = %s, name = %s' \
            % (self.short_name, self.id, self.current_media_obj[0].file_name))
        self.player.set_media(self.media)
        if self.player_mode == 0:
            self.stream = self.player.file_read_slow()
        elif self.player_mode == 1:
            self.stream = self.player.file_read_fast()

    def set_webm_read_mode(self):
        self.channel.set_callback(FileReader(self.media).read_callback)

    def update_twitter_current(self):
        artist_names = self.artist.split(' ')
        artist_tags = ' #'.join(list(set(artist_names)-set(['&', '-'])))
        message = '%s %s on #%s' % (self.prefix, self.song, self.short_name)
        tags = '#' + ' #'.join(self.twitter_tags)
        message = message + ' ' + tags
        message = message[:108] + ' M3U: ' + self.m3u_tinyurl
        self.update_twitter(message)

    def channel_open(self):
        self.channel.open()
        self.channel_delay = self.channel.delay()

    def ping_server(self):
        log = True
        while not self.server_ping:
            try:
                self.q.get(1)
                server = urllib.urlopen(self.server_url)
                self.server_ping = True
                self.logger.write_info('Station ' + self.channel_url + ' : channel available')
                self.q.task_done()
            except:
                time.sleep(0.5)
                if log:
                    self.logger.write_error('Station ' + self.channel_url + ' : could not connect the channel' )
                    log = False
                self.q.task_done()
                pass

    def run(self):
        self.q.get(1)
        self.ping_server()
        self.q.task_done()

        if self.type == 'stream-m':
            self.q.get(1)
            if self.relay_mode:
                self.set_relay_mode()
            else:
                self.media = self.get_next_media()
                self.set_webm_read_mode()
            self.channel_open()
            self.channel.start()
            self.q.task_done()

        if self.type == 'icecast':
            self.q.get(1)
            self.channel_open()
            self.logger.write_info('Station ' + self.channel_url + ' : channel connected')
            self.q.task_done()

            while self.run_mode:
                self.q.get(1)
                self.next_media = 0
                self.media = self.get_next_media()
                self.counter += 1
                if self.relay_mode:
                    self.set_relay_mode()
                elif os.path.exists(self.media) and not os.sep+'.' in self.media:
                    if self.lp == 0:
                        self.logger.write_error('Station ' + self.channel_url + ' : has no media to stream !')
                        break
                    self.set_read_mode()
                self.q.task_done()

                self.q.get(1)
                if (not (self.jingles_mode and (self.counter % 2)) or self.relay_mode) and self.twitter_mode:
                    try:
                        self.update_twitter_current()
                    except:
                        continue
                try:
                    self.channel.set_metadata({'song': self.song, 'charset': 'utf-8',})
                except:
                    continue
                self.q.task_done()


                for self.chunk in self.stream:
                    if self.next_media or not self.run_mode:
                        break
                    if self.record_mode:
                        try:
                            self.q.get(1)
                            self.recorder.write(self.chunk)
                            self.q.task_done()
                        except:
                            self.logger.write_error('Station ' + self.channel_url + ' : could not write the buffer to the file')
                            self.q.task_done()
                            continue
                    try:
                        self.q.get(1)
                        self.channel.send(self.chunk)
                        self.channel.sync()
                        self.q.task_done()
                    except:
                        self.logger.write_error('Station ' + self.channel_url + ' : could not send the buffer')
                        self.q.task_done()
                        try:
                            self.q.get(1)
                            self.channel.close()
                            self.logger.write_info('Station ' + self.channel_url + ' : channel closed')
                            self.q.task_done()
                        except:
                            self.logger.write_error('Station ' + self.channel_url + ' : could not close the channel')
                            self.q.task_done()
                            continue
                        try:
                            self.ping_server()
                            self.q.get(1)
                            self.channel_open()
                            self.channel.set_metadata({'song': self.song, 'charset': 'utf8',})
                            self.logger.write_info('Station ' + self.channel_url + ' : channel restarted')
                            self.q.task_done()
                        except:
                            self.logger.write_error('Station ' + self.channel_url + ' : could not restart the channel')
                            self.q.task_done()
                            continue
                        continue

            if self.record_mode:
                self.recorder.close()

            self.channel.close()






