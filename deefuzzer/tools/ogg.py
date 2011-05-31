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
import string
import datetime
from mutagen.oggvorbis import OggVorbis
from tools import *


class Ogg:
    """An OGG file object"""

    def __init__(self, media):
        self.media = media
        self.ogg = OggVorbis(self.media)
        self.item_id = ''
        self.source = self.media
        self.options = {}
        self.bitrate_default = '192'
        self.cache_dir = os.sep + 'tmp'
        self.keys2ogg = {'title': 'title',
                    'artist': 'artist',
                    'album': 'album',
                    'date': 'date',
                    'comment': 'comment',
                    'genre': 'genre',
                    'copyright': 'copyright',
                    }
        self.info = self.ogg.info
        self.bitrate = int(str(self.info.bitrate)[:-3])
        self.length = datetime.timedelta(0,self.info.length)
        self.metadata = self.get_file_metadata()
        self.description = self.get_description()
        self.mime_type = self.get_mime_type()
        self.media_info = get_file_info(self.media)
        self.file_name = self.media_info[0]
        self.file_title = self.media_info[1]
        self.file_ext = self.media_info[2]
        self.extension = self.get_file_extension()
        self.size = os.path.getsize(media)
        #self.args = self.get_args()

    def get_format(self):
        return 'OGG'

    def get_file_extension(self):
        return 'ogg'

    def get_mime_type(self):
        return 'application/ogg'

    def get_description(self):
        return 'FIXME'

    def get_file_info(self):
        try:
            file_out1, file_out2 = os.popen4('ogginfo "'+self.dest+'"')
            info = []
            for line in file_out2.readlines():
                info.append(clean_word(line[:-1]))
            self.info = info
            return self.info
        except:
            raise IOError('ExporterError: file does not exist.')

    def set_cache_dir(self,path):
       self.cache_dir = path

    def get_file_metadata(self):
        metadata = {}
        for key in self.keys2ogg.keys():
            try:
                metadata[key] = self.ogg[key][0]
            except:
                metadata[key] = ''
        return metadata

    def decode(self):
        try:
            os.system('oggdec -o "'+self.cache_dir+os.sep+self.item_id+
                      '.wav" "'+self.source+'"')
            return self.cache_dir+os.sep+self.item_id+'.wav'
        except:
            raise IOError('ExporterError: decoder is not compatible.')

    def write_tags(self):
        #self.ogg.add_tags()
        for tag in self.metadata.keys():
            self.ogg[tag] = str(self.metadata[tag])
        self.ogg.save()

    def get_args(self,options=None):
        """Get process options and return arguments for the encoder"""
        args = []
        if not options is None:
            self.options = options
            if not ('verbose' in self.options and self.options['verbose'] != '0'):
                args.append('-Q ')
            if 'ogg_bitrate' in self.options:
                args.append('-b '+self.options['ogg_bitrate'])
            elif 'ogg_quality' in self.options:
                args.append('-q '+self.options['ogg_quality'])
            else:
                args.append('-b '+self.bitrate_default)
        else:
            args.append('-Q -b '+self.bitrate_default)

        for tag in self.metadata.keys():
            value = clean_word(self.metadata[tag])
            args.append('-c %s="%s"' % (tag, value))
            if tag in self.dub2args_dict.keys():
                arg = self.dub2args_dict[tag]
                args.append('-c %s="%s"' % (arg, value))

        return args
