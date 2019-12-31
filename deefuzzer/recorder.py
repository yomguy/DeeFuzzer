#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2006-2009 Guillaume Pellerin

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



import os


class Recorder:
    """A file streaming iterator"""

    def __init__(self, path):
        self.path = path
        self.recording = True

    def open(self, filename):
        self.filename = filename
        self.media = open(self.path + os.sep + self.filename, 'w')

    def write(self, chunk):
        try:
            if self.recording:
                self.media.write(chunk)
                self.media.flush()
        except:
            pass

    def close(self):
        self.media.close()
