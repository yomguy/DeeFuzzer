#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2006-2011 Guillaume Pellerin

# <yomguy@parisson.com>

# This file is part of deefuzzer

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


from threading import Thread
import queue
import urllib.request, urllib.parse, urllib.error


class Relay(Thread):

    def __init__(self, sub_buffer_size, queue_size):
        Thread.__init__(self)
        self.sub_buffer_size = sub_buffer_size
        self.queue_size = queue_size
        self.queue = queue.Queue(self.queue_size)
        self.stream = None

    def set_url(self, url):
        self.url = url

    def open(self):
        try:
            self.stream = urllib.request.urlopen(self.url)
            self.isopen = True
        except:
            self.isopen = False

    def close(self):
        if self.stream:
            self.isopen = False

    def run(self):
        while True:
            if self.isopen:
                self.chunk = self.stream.read(self.sub_buffer_size)
                self.queue.put_nowait(self.chunk)
#                print self.queue.qsize()
            else:
                if self.stream:
                    self.stream.close()
                else:
                    self.open()

