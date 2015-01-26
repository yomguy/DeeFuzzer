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
    _delay = 0

    def __init__(self):
        Thread.__init__(self)
        import pycurl

        self.curl = pycurl.Curl()

    def set_callback(self, read_callback):
        self.read_callback = read_callback

    def delay(self):
        return self._delay

    def open(self):
        import pycurl

        self.uri = self.protocol + '://' + self.host + ':' + str(self.port)
        self.uri += self.mount + '?' + 'password=' + self.password
        self.curl.setopt(pycurl.URL, self.uri)
        self.curl.setopt(pycurl.NOSIGNAL, 1)
        self.curl.setopt(pycurl.UPLOAD, 1)
        self.curl.setopt(pycurl.READFUNCTION, self.read_callback)

    def run(self):
        self.curl.perform()

    def close(self):
        self.curl.close()
