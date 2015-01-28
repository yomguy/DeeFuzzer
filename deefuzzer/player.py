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

from relay import *
import time


class Player:
    """A file streaming iterator"""

    def __init__(self, stream_type='icecast'):
        if stream_type == 'icecast':
            self.main_buffer_size = 0x100000
            self.relay_queue_size = 0x100000
            self.sub_buffer_size = 0x10000
        elif stream_type == 'stream-m':
            self.main_buffer_size = 0x100000
            self.relay_queue_size = 0x100000
            self.sub_buffer_size = 0x10000

    def set_media(self, media):
        self.media = media

    def start_relay(self, url):
        self.url = url
        self.relay = Relay(self.sub_buffer_size, self.relay_queue_size)
        self.relay.set_url(self.url)
        self.relay.open()
        self.relay.start()
        self.queue = self.relay.queue

    def stop_relay(self):
        self.relay.close()

    def file_read_fast(self):
        """Read media and stream data through a generator."""
        m = open(self.media, 'r')
        while True:
            __main_chunk = m.read(self.sub_buffer_size)
            if not __main_chunk:
                break
            yield __main_chunk
        m.close()

    def file_read_slow(self):
        """Read a bigger part of the media and stream the little parts
         of the data through a generator"""
        m = open(self.media, 'r')
        while True:
            self.main_chunk = m.read(self.main_buffer_size)
            if not self.main_chunk:
                break
            i = 0
            while True:
                start = i * self.sub_buffer_size
                end = self.sub_buffer_size + (i * self.sub_buffer_size)
                self.sub_chunk = self.main_chunk[start:end]
                if not self.sub_chunk:
                    break
                yield self.sub_chunk
                i += 1
        self.main_chunk = 0
        self.sub_chunk = 0
        m.close()

    def relay_read(self):
        """Read a distant media through its URL"""
        while True:
            self.sub_chunk = self.queue.get(self.sub_buffer_size)
            if not self.sub_chunk:
                break
            yield self.sub_chunk
            self.queue.task_done()
        self.sub_chunk = 0


class FileReader:

    def __init__(self, fp):
        self.fp = open(fp, 'r')

    def read_callback(self, size):
        return self.fp.read(size)


class URLReader:

    def __init__(self, relay):
        self.__relayparam = relay
        self.relay = urllib.urlopen(self.__relayparam)
        self.rec_mode = 0

    def set_recorder(self, recorder, mode=1):
        self.rec_mode = mode
        self.recorder = recorder

    def read_callback(self, size):
        chunk = None

        try:
            chunk = self.relay.read(size)
        except:
            while True:
                try:
                    self.relay = urllib.urlopen(self.__relayparam)
                    chunk = self.relay.read(size)
                    break
                except:
                    time.sleep(0.5)
                    continue

        if self.rec_mode == 1 and chunk:
            self.recorder.write(chunk)
        return chunk
