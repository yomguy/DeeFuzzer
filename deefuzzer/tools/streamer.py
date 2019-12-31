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


class HTTPStreamer(Thread):
    protocol = 'http'
    host = str
    port = str
    mount = str
    user = str
    password = str
    public = str
    audio_info = dict
    name = str
    genre = str
    decription = str
    format = str
    url = str
    delay = 0

    def __init__(self):
        Thread.__init__(self)
        import pycurl

        self.curl = pycurl.Curl()

    def set_callback(self, read_callback):
        self.read_callback = read_callback

    def delay(self):
        return self.delay

    def open(self):
        import pycurl

        self.uri = self.protocol + '://' + self.host + ':' + str(self.port)
        self.uri += self.mount + '?' + 'password=' + self.password
        self.curl.setopt(pycurl.URL, self.uri)
        self.curl.setopt(pycurl.UPLOAD, 1)
        self.curl.setopt(pycurl.READFUNCTION, self.read_callback)

    def run(self):
        self.curl.perform()

    def close(self):
        self.curl.close()
