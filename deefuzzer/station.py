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
import json

from threading import Thread
from player import *
from recorder import *
from relay import *
from streamer import *
from tools import *


class Station(Thread):
    """a DeeFuzzer shouting station thread"""

    id = 999999
    counter = 0
    delay = 0
    start_time = time.time()
    server_ping = False
    playlist = []
    lp = 1
    player_mode = 0
    osc_control_mode = 0
    twitter_mode = 0
    jingles_mode = 0
    relay_mode = 0
    record_mode = 0
    run_mode = 1
    station_dir = None
    appendtype = 1
    feeds_json = 0
    feeds_rss = 1
    feeds_mode = 1
    feeds_playlist = 1
    feeds_showfilepath = 0
    feeds_showfilename = 0
    short_name = ''

    def __init__(self, station, q, logqueue, m3u):
        Thread.__init__(self)
        self.station = station
        self.q = q
        self.logqueue = logqueue
        self.m3u = m3u

        if 'station_dir' in self.station:
            self.station_dir = self.station['station_dir']

        # Media
        self.media_dir = self.station['media']['dir']
        self.media_format = self.station['media']['format']
        self.shuffle_mode = int(self.station['media']['shuffle'])
        self.bitrate = int(self.station['media']['bitrate'])
        self.ogg_quality = int(self.station['media']['ogg_quality'])
        self.samplerate = int(self.station['media']['samplerate'])
        self.voices = int(self.station['media']['voices'])
        self.m3u_playlist_file = []
        if 'm3u' in self.station['media'].keys():
            self.m3u_playlist_file = self.station['media']['m3u']

        # Server
        if 'mountpoint' in self.station['server'].keys():
            self.mountpoint = self.station['server']['mountpoint']
        elif 'short_name' in self.station['infos'].keys():
            self.mountpoint = self.station['infos']['short_name']
        else:
            self.mountpoint = 'default'

        self.short_name = self.mountpoint

        if 'appendtype' in self.station['server'].keys():
            self.appendtype = int(self.station['server']['appendtype'])

        if 'type' in self.station['server']:
            self.type = self.station['server']['type'] #  'icecast' | 'stream-m'
        else:
            self.type = 'icecast'

        if 'stream-m' in self.type:
            self.channel = HTTPStreamer()
            self.channel.mount = '/publish/' + self.mountpoint
        elif 'icecast' in self.type:
            self.channel = shout.Shout()
            self.channel.mount = '/' + self.mountpoint
            if self.appendtype:
                self.channel.mount = self.channel.mount + '.' + self.media_format
        else:
            sys.exit('Not a compatible server type. Choose "stream-m" or "icecast".')

        self.channel.url = self.station['infos']['url']
        self.channel.name = self.station['infos']['name']
        self.channel.genre = self.station['infos']['genre']
        self.channel.description = self.station['infos']['description']
        self.channel.format = self.media_format
        self.channel.host = self.station['server']['host']
        self.channel.port = int(self.station['server']['port'])
        self.channel.user = 'source'
        self.channel.password = self.station['server']['sourcepassword']
        self.channel.public = int(self.station['server']['public'])
        if self.channel.format == 'mp3':
            self.channel.audio_info = { 'bitrate': str(self.bitrate),
                                        'samplerate': str(self.samplerate),
                                        'channels': str(self.voices),}
        else:
            self.channel.audio_info = { 'bitrate': str(self.bitrate),
                                        'samplerate': str(self.samplerate),
                                        'quality': str(self.ogg_quality),
                                        'channels': str(self.voices),}

        self.server_url = 'http://' + self.channel.host + ':' + str(self.channel.port)
        self.channel_url = self.server_url + self.channel.mount

        # RSS
        if 'feeds' in self.station:
            self.station['rss'] = self.station['feeds']

        if 'rss' in self.station:
            if 'mode' in self.station['rss']:
                self.feeds_mode = int(self.station['rss']['mode'])
            self.feeds_dir = self.station['rss']['dir']
            self.feeds_enclosure = int(self.station['rss']['enclosure'])
            if 'json' in self.station['rss']:
                self.feeds_json = int(self.station['rss']['json'])
            if 'rss' in self.station['rss']:
                self.feeds_rss = int(self.station['rss']['rss'])
            if 'playlist' in self.station['rss']:
                self.feeds_playlist = int(self.station['rss']['playlist'])
            if 'showfilename' in self.station['rss']:
                self.feeds_showfilename = int(self.station['rss']['showfilename'])
            if 'showfilepath' in self.station['rss']:
                self.feeds_showfilepath = int(self.station['rss']['showfilepath'])

            self.feeds_media_url = self.channel.url + '/media/'
            if 'media_url' in self.station['rss']:
                if not self.station['rss']['media_url'] == '':
                    self.feeds_media_url = self.station['rss']['media_url']

        self.base_name = self.feeds_dir + os.sep + self.short_name + '_' + self.channel.format
        self.feeds_current_file = self.base_name + '_current'
        self.feeds_playlist_file = self.base_name + '_playlist'

        # Logging
        self._info('Opening ' + self.short_name + ' - ' + self.channel.name)

        self.metadata_relative_dir = 'metadata'
        self.metadata_url = self.channel.url + '/rss/' + self.metadata_relative_dir
        self.metadata_dir = self.feeds_dir + os.sep + self.metadata_relative_dir
        if not os.path.exists(self.metadata_dir):
            os.makedirs(self.metadata_dir)

        # The station's player
        self.player = Player(self.type)

        # OSCing
        # mode = 0 means Off, mode = 1 means On
        if 'control' in self.station:
            self.osc_control_mode = int(self.station['control']['mode'])
            if self.osc_control_mode:
                self.osc_port = int(self.station['control']['port'])
                self.osc_controller = OSCController(self.osc_port)
                # OSC paths and callbacks
                self.osc_controller.add_method('/media/next', 'i', self.media_next_callback)
                self.osc_controller.add_method('/media/relay', 'i', self.relay_callback)
                self.osc_controller.add_method('/twitter', 'i', self.twitter_callback)
                self.osc_controller.add_method('/jingles', 'i', self.jingles_callback)
                self.osc_controller.add_method('/record', 'i', self.record_callback)
                self.osc_controller.add_method('/player', 'i', self.player_callback)
                self.osc_controller.add_method('/run', 'i', self.run_callback)
                self.osc_controller.start()

        # Jingling between each media.
        if 'jingles' in self.station:
            self.jingles_mode =  int(self.station['jingles']['mode'])
            self.jingles_shuffle = int(self.station['jingles']['shuffle'])
            self.jingles_dir = self.station['jingles']['dir']
            if self.jingles_mode == 1:
                self.jingles_callback('/jingles', [1])

        # Relaying
        if 'relay' in self.station:
            self.relay_mode = int(self.station['relay']['mode'])
            self.relay_url = self.station['relay']['url']
            self.relay_author = self.station['relay']['author']
            if self.relay_mode == 1:
                self.relay_callback('/media/relay', [1])

        # Twitting
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

            if self.twitter_mode:
                self.twitter_callback('/twitter', [1])

        # Recording
        if 'record' in self.station:
            self.record_mode = int(self.station['record']['mode'])
            self.record_dir = self.station['record']['dir']
            if self.record_mode:
                self.record_callback('/record', [1])

    def _log(self, level, msg):
        try:
            obj = {}
            obj['msg'] = 'Station ' + str(self.channel_url) + ': ' + str(msg)
            obj['level'] = str(level)
            self.logqueue.put(obj)
        except:
            pass
    
    def _info(self, msg):
        self._log('info', msg)
    
    def _err(self, msg):
        self._log('err', msg)
    
    def run_callback(self, path, value):
        value = value[0]
        self.run_mode = value
        message = "received OSC message '%s' with arguments '%d'" % (path, value)
        self._info(message)

    def media_next_callback(self, path, value):
        value = value[0]
        self.next_media = value
        message = "received OSC message '%s' with arguments '%d'" % (path, value)
        self._info(message)

    def relay_callback(self, path, value):
        value = value[0]
        if value:
            self.relay_mode = 1
            if self.type == 'icecast':
                self.player.start_relay(self.relay_url)
        else:
            self.relay_mode = 0
            if self.type == 'icecast':
                self.player.stop_relay()

        self.id = 0
        self.next_media = 1
        message = "received OSC message '%s' with arguments '%d'" % (path, value)
        self._info(message)
        message = "relaying : %s" % self.relay_url
        self._info(message)

    def twitter_callback(self, path, value):
        value = value[0]
        self.twitter = Twitter(self.twitter_key, self.twitter_secret)
        self.twitter_mode = value
        message = "received OSC message '%s' with arguments '%d'" % (path, value)
        self.m3u_url = self.channel.url + '/m3u/' + self.m3u.split(os.sep)[-1]
        self.feeds_url = self.channel.url + '/rss/' + self.feeds_playlist_file.split(os.sep)[-1]
        self._info(message)

    def jingles_callback(self, path, value):
        value = value[0]
        if value:
            self.jingles_list = self.get_jingles()
            self.jingles_length = len(self.jingles_list)
            self.jingle_id = 0
        self.jingles_mode = value
        message = "received OSC message '%s' with arguments '%d'" % (path, value)
        self._info(message)

    def record_callback(self, path, value):
        value = value[0]
        if value:
            if not os.path.exists(self.record_dir):
                os.makedirs(self.record_dir)
            self.rec_file = self.short_name.replace('/', '_') + '-' + \
              datetime.datetime.now().strftime("%x-%X").replace('/', '_') + \
                                                '.' + self.channel.format
            self.recorder = Recorder(self.record_dir)
            self.recorder.open(self.rec_file)
        else:
            try:
                self.recorder.recording = False
                self.recorder.close()
            except:
                pass
                
            if self.type == 'icecast':
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
        message = "received OSC message '%s' with arguments '%d'" % (path, value)
        self._info(message)

    def player_callback(self, path, value):
        value = value[0]
        self.player_mode = value
        message = "received OSC message '%s' with arguments '%d'" % (path, value)
        self._info(message)

    def get_playlist(self):
        file_list = []
        if not self.m3u_playlist_file:
            for root, dirs, files in os.walk(self.media_dir):
                for file in files:
                    s = file.split('.')
                    ext = s[len(s)-1]
                    if ext.lower() == self.channel.format and not os.sep+'.' in file:
                        file_list.append(root + os.sep + file)
            file_list.sort()
        else:
            self.q.get(1)
            try:
                f = open(self.m3u_playlist_file, 'r')
                try:
                    for path in f.readlines():
                        if '#' != path[0]:
                            file_list.append(path[:-1])
                except:
                    f.close()
            except:
                pass
            self.q.task_done()
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

    def tweet(self):
        if len(self.new_tracks):
            new_tracks_objs = self.media_to_objs(self.new_tracks)
            for media_obj in new_tracks_objs:
                title = ''
                artist = ''
                if media_obj.metadata.has_key('title'):
                    title = media_obj.metadata['title']
                if media_obj.metadata.has_key('artist'):
                    artist = media_obj.metadata['artist']
                if not (title or artist):
                    song = str(media_obj.file_name)
                else:
                    song = artist + ' - ' + title
                    song = song.encode('utf-8')
                    artist = artist.encode('utf-8')

                    artist_names = artist.split(' ')
                    artist_tags = ' #'.join(list(set(artist_names)-set(['&', '-'])))
                    message = '#NEWTRACK ! %s #%s on #%s RSS: ' % \
                             (song.replace('_', ' '), artist_tags, self.short_name)
                    message = message[:113] + self.feeds_url
                    self.update_twitter(message)

    def get_next_media(self):
        # Init playlist
        if self.lp:
            playlist = self.playlist
            new_playlist = self.get_playlist()
            lp_new = len(new_playlist)

            if not self.counter:
                self.id = 0
                self.playlist = new_playlist
                self.lp = lp_new

                # Shake it, Fuzz it !
                if self.shuffle_mode:
                    random.shuffle(self.playlist)

                self._info('Generating new playlist (' + str(self.lp) + ' tracks)')

                if self.feeds_playlist:
                    self.update_feeds(self.media_to_objs(self.playlist), self.feeds_playlist_file, '(playlist)')

            elif lp_new != self.lp:
                self.id = 0
                self.lp = lp_new

                # Twitting new tracks
                new_playlist_set = set(new_playlist)
                playlist_set = set(playlist)
                new_tracks = new_playlist_set - playlist_set
                self.new_tracks = list(new_tracks.copy())

                if self.twitter_mode == 1  and self.counter:
                    self.tweet()

                # Shake it, Fuzz it !
                if self.shuffle_mode:
                    random.shuffle(playlist)

                # Play new tracks first
                for track in self.new_tracks:
                    playlist.insert(0, track)

                self.playlist = playlist

                self._info('generating new playlist (' + str(self.lp) + ' tracks)')

                if self.feeds_playlist:
                    self.update_feeds(self.media_to_objs(self.playlist), self.feeds_playlist_file, '(playlist)')

            if self.jingles_mode and not (self.counter % 2) and self.jingles_length:
                media = self.jingles_list[self.jingle_id]
                self.jingle_id = (self.jingle_id + 1) % self.jingles_length
            else:
                media = self.playlist[self.id]
                self.id = (self.id + 1) % self.lp
            return media
        else:
            mess = 'No media in media_dir !'
            self._err(mess)
            self.run_mode = 0

    def media_to_objs(self, media_list):
        media_objs = []
        for media in media_list:
            file_name, file_title, file_ext = get_file_info(media)
            self.q.get(1)
            try:
                if file_ext.lower() == 'mp3' or mimetypes.guess_type(media)[0] == 'audio/mpeg':
                    try:
                        file_meta = Mp3(media)
                    except:
                        continue
                elif file_ext.lower() == 'ogg' or mimetypes.guess_type(media)[0] == 'audio/ogg':
                    try:
                        file_meta = Ogg(media)
                    except:
                        continue
                elif file_ext.lower() == 'webm' or mimetypes.guess_type(media)[0] == 'video/webm':
                    try:
                        file_meta = WebM(media)
                    except:
                        continue
                if self.feeds_showfilename:
                    file_meta.metadata['filename'] = file_name.decode( "utf-8" )   #decode needed for some weird filenames
                if self.feeds_showfilepath:
                    file_meta.metadata['filepath'] = media.decode( "utf-8" )   #decode needed for some weird filenames
            except:
                pass
            self.q.task_done()
            media_objs.append(file_meta)
        return media_objs

    def update_feeds(self, media_list, rss_file, sub_title):
        if not self.feeds_mode:
            return
            
        rss_item_list = []
        if not os.path.exists(self.feeds_dir):
            os.makedirs(self.feeds_dir)
        channel_subtitle = self.channel.name + ' ' + sub_title
        _date_now = datetime.datetime.now()
        date_now = str(_date_now)
        media_absolute_playtime = _date_now
        json_data = []

        for media in media_list:
            json_item = {}
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
                    media_description += media_description_item % (key.capitalize(),
                                                                   media.metadata[key])
                    json_item[key] = media.metadata[key]
            media_description += '</table>'

            title = media.metadata['title']
            artist = media.metadata['artist']
            if not (title or artist):
                song = str(media.file_title)
            else:
                song = artist + ' - ' + title

            media_absolute_playtime += media.length

            if self.feeds_enclosure == '1':
                media_link = self.feeds_media_url + media.file_name
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
            json_data.append(json_item)

        rss = RSS2(title = channel_subtitle, \
                            link = self.channel.url, \
                            description = self.channel.description.decode('utf-8'), \
                            lastBuildDate = date_now, \
                            items = rss_item_list,)
        self.q.get(1)
        try:
            if self.feeds_rss:
                f = open(rss_file + '.xml', 'w')
                rss.write_xml(f, 'utf-8')
                f.close()

            if self.feeds_json:
                f = open(rss_file + '.json', 'w')
                f.write(json.dumps(json_data, separators=(',',':')))
                f.close()
        except:
            pass
        self.q.task_done()

    def update_twitter(self, message):
        try:
            self.twitter.post(message.decode('utf8'))
            self._info('Twitting : "' + message + '"')
        except:
            self._err('Twitting : "' + message + '"')

    def set_relay_mode(self):
        self.prefix = '#nowplaying #LIVE'
        self.title = self.channel.description.encode('utf-8')
        self.artist = self.relay_author.encode('utf-8')
        self.title = self.title.replace('_', ' ')
        self.artist = self.artist.replace('_', ' ')
        self.song = self.artist + ' - ' + self.title

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
        try:
            self.title = self.current_media_obj[0].metadata['title']
            self.artist = self.current_media_obj[0].metadata['artist']
        except:
            self.title = 'title'
            self.artist = 'artist'

        self.title = self.title.replace('_', ' ')
        self.artist = self.artist.replace('_', ' ')

        if not (self.title or self.artist):
            song = str(self.current_media_obj[0].file_name)
        else:
            song = self.artist + ' - ' + self.title

        self.song = song.encode('utf-8')
        self.artist = self.artist.encode('utf-8')
        self.metadata_file = self.metadata_dir + os.sep + self.current_media_obj[0].file_name + '.xml'
        self.update_feeds(self.current_media_obj, self.feeds_current_file, '(currently playing)')
        self._info('DeeFuzzing:  id = %s, name = %s' \
            % (self.id, self.current_media_obj[0].file_name))
        self.player.set_media(self.media)

        self.q.get(1)
        try:
            if self.player_mode:
                self.stream = self.player.file_read_slow()
            else:
                self.stream = self.player.file_read_fast()
        except:
            pass
        self.q.task_done()

    def set_webm_read_mode(self):
        self.channel.set_callback(FileReader(self.media).read_callback)

    def update_twitter_current(self):
        artist_names = self.artist.split(' ')
        artist_tags = ' #'.join(list(set(artist_names)-set(['&', '-'])))
        message = '%s %s on #%s' % (self.prefix, self.song, self.short_name)
        tags = '#' + ' #'.join(self.twitter_tags)
        message = message + ' ' + tags
        message = message[:108] + ' M3U: ' + self.m3u_url
        self.update_twitter(message)

    def channel_open(self):
        self.channel.open()
        self.channel_delay = self.channel.delay()

    def ping_server(self):
        log = True

        while not self.server_ping:
            try:
                server = urllib.urlopen(self.server_url)
                self.server_ping = True
                self._info('Channel available.')
            except:
                time.sleep(1)
                if log:
                    self._err('Could not connect the channel.  Waiting for channel to become available.')
                    log = False

    def icecastloop_nextmedia(self):
        try:
            self.next_media = 0
            self.media = self.get_next_media()
            self.counter += 1
            if self.relay_mode:
                self.set_relay_mode()
            elif os.path.exists(self.media) and not os.sep+'.' in self.media:
                if self.lp == 0:
                    self._err('has no media to stream !')
                    return False
                self.set_read_mode()
            
            return True
        except Exception, e:
            self_err('icecastloop_nextmedia: Error: ' + str(e))
        return False
    
    def icecastloop_metadata(self):
        try:
            if (not (self.jingles_mode and (self.counter % 2)) or \
                                self.relay_mode) and self.twitter_mode:
                self.update_twitter_current()
            self.channel.set_metadata({'song': self.song, 'charset': 'utf-8'})
            return True
        except Exception, e:
            self_err('icecastloop_metadata: Error: ' + str(e))
        return False

    def run(self):
        self.ping_server()

        if self.type == 'stream-m':
            if self.relay_mode:
                self.set_relay_mode()
            else:
                self.media = self.get_next_media()
                self.set_webm_read_mode()
            self.channel_open()
            self.channel.start()

        if self.type == 'icecast':
            self.channel_open()
            self._info('channel connected')

            while self.run_mode:
                if not self.icecastloop_nextmedia():
                    self._info('Something wrong happened in icecastloop_nextmedia.  Ending.')
                    break
                    
                self.icecastloop_metadata()

                # TEST MODE: Jump thru only the first chunk of each file
                # first = True
                for self.chunk in self.stream:
                    # if first:
                    #     first = False
                    # else:
                    #     break
                    
                    if self.next_media or not self.run_mode:
                        break
                    
                    if self.record_mode:
                        try:
                            # Record the chunk
                            self.recorder.write(self.chunk)
                        except:
                            self._err('could not write the buffer to the file')
                            continue
                                
                    try:
                        # Send the chunk to the stream
                        self.channel.send(self.chunk)
                        self.channel.sync()
                    except:
                        self._err('could not send the buffer')
                        
                        try:
                            self.channel.close()
                            self._info('channel closed')
                        except:
                            self._err('could not close the channel')
                            self.q.task_done()
                            continue
                            
                        try:
                            self.ping_server()
                            self.channel_open()
                            self.channel.set_metadata({'song': self.song, 'charset': 'utf8',})
                            self._info('channel restarted')
                        except:
                            self._err('could not restart the channel')
                            if self.record_mode:
                                self.recorder.close()
                            return
                            
                        try:
                            self.channel.send(self.chunk)
                            self.channel.sync()
                        except:
                            self._err('could not send data after restarting the channel')
                            try:
                                self.channel.close()
                            except:
                                self._err('could not close the channel')
                                
                            if self.record_mode:
                                self.recorder.close()
                            return
                            
                # send chunk loop end
            # while run_mode loop end
            
            self._info("Play mode ended. Stopping stream.")
            
            if self.record_mode:
                self.recorder.close()

            self.channel.close()

