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
import Queue
import urllib


class Relay(Thread):

    def __init__(self, sub_buffer_size, queue_size):
        Thread.__init__(self)
        self.sub_buffer_size = sub_buffer_size
        self.queue_size = queue_size
        self.queue = Queue.Queue(self.queue_size)
        self.stream = None

    def set_url(self, url):
        self.url = url

    def open(self):
        try:
            self.stream = urllib.urlopen(self.url)
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

