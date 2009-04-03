# -*- coding: utf-8 -*-
#
# Copyright (c) 2006-2009 Guillaume Pellerin <pellerin@parisson.com>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution. The terms
# are also available at http://svn.parisson.org/telemeta/TelemetaLicense.
#
# Author: Guillaume Pellerin <pellerin@parisson.com>

import os
import string
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3

EasyID3.valid_keys["comment"]="COMM::'XXX'"

class Mp3:
    """An MP3 file object"""
    
    def __init__(self, media):
        self.media = media
        self.item_id = ''
        self.source = self.media
        self.options = {}
        self.bitrate_default = '192'
        self.cache_dir = os.sep + 'tmp'
        self.keys2id3 = {'title': 'TIT2',
                    'artist': 'TPE1',
                    'album': 'TALB',
                    'date': 'TDRC',
                    'comment': 'COMM',
                    'genre': 'TCON',
                    }
        self.metadata = self.get_metadata()
        self.description = self.get_description()
        self.mime_type = self.get_mime_type()
        self.extension = self.get_file_extension()
        self.size = os.path.getsize(media)
        self.file_name = media.split(os.sep)[-1]
        #self.args = self.get_args()
                    
    def get_format(self):
        return 'MP3'
    
    def get_file_extension(self):
        return 'mp3'

    def get_mime_type(self):
        return 'audio/mpeg'

    def get_description(self):
        return "MPEG audio Layer III"
    
    def get_metadata(self):
        m = MP3(self.media, ID3=EasyID3)
        metadata = {}
        for key in self.keys2id3.keys():
            try:
                metadata[key] = m[key][0]
            except:
                metadata[key] = ''
        return metadata

    def decode(self):
        try:
            os.system('sox "'+self.media+'" -s -q -r 44100 -t wav "' \
                        +self.cache_dir+os.sep+self.item_id+'"')
            return self.cache_dir+os.sep+self.metadata['title']+'.wav'
        except:
            raise IOError('ExporterError: decoder is not compatible.')

    def write_tags(self):
        """Write all ID3v2.4 tags by mapping dub2id3_dict dictionnary with the
            respect of mutagen classes and methods"""
        id3 = id3.ID3(self.media)
        for tag in self.metadata.keys():
            if tag in self.dub2id3_dict.keys():
                frame_text = self.dub2id3_dict[tag]
                value = self.metadata[tag]
                frame = mutagen.id3.Frames[frame_text](3,value)
                try:
                    id3.add(frame)
                except:
                    raise IOError('ExporterError: cannot tag "'+tag+'"')
        try:
            id3.save()
        except:
            raise IOError('ExporterError: cannot write tags')

    def get_args(self, options=None):
        """Get process options and return arguments for the encoder"""
        args = []
        if not options is None: 
            self.options = options
            if not ( 'verbose' in self.options and self.options['verbose'] != '0' ):
                args.append('-S')
            if 'mp3_bitrate' in self.options:
                args.append('-b ' + self.options['mp3_bitrate'])
            else:
                args.append('-b '+self.bitrate_default)
            #Copyrights, etc..
            args.append('-c -o')
        else:
            args.append('-S -c -o')

        for tag in self.metadata.keys():
            if tag in self.dub2args_dict.keys():
                arg = self.dub2args_dict[tag]
                value = self.metadata[tag]
                args.append('--' + arg)
                args.append('"' + value + '"')

        return args

