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
from mutagen.oggvorbis import OggVorbis

class Ogg:
    """An OGG file object"""
    
    def __init__(self, media):
        self.item_id = ''
        self.metadata = {}
        self.description = ''
        self.info = []
        self.source = ''
        self.dest = ''
        self.options = {}
        self.bitrate_default = '192'
        self.buffer_size = 0xFFFF
        self.dub2args_dict = {'creator': 'artist',
                             'relation': 'album'
                             }
        
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

    def decode(self):
        try:
            os.system('oggdec -o "'+self.cache_dir+os.sep+self.item_id+
                      '.wav" "'+self.source+'"')
            return self.cache_dir+os.sep+self.item_id+'.wav'
        except:
            raise IOError('ExporterError: decoder is not compatible.')

    def write_tags(self):
        media = OggVorbis(self.dest)
        for tag in self.metadata.keys():
            media[tag] = str(self.metadata[tag])
        media.save()

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

    def process(self, item_id, source, metadata, options=None):
        self.item_id = item_id
        self.source = source
        self.metadata = metadata
        self.args = self.get_args(options)
        self.ext = self.get_file_extension()
        self.args = ' '.join(self.args)
        self.command = 'sox "%s" -s -q -r 44100 -t wav -c2 - | oggenc %s -' % (self.source, self.args)

        # Pre-proccessing
        self.dest = self.pre_process(self.item_id,
                                        self.source,
                                        self.metadata,
                                        self.ext,
                                        self.cache_dir,
                                        self.options)

        # Processing (streaming + cache writing)
        stream = self.core_process(self.command, self.buffer_size, self.dest)
        for chunk in stream:
            yield chunk
    
        # Post-proccessing
        #self.post_process(self.item_id,
                        #self.source,
                        #self.metadata,
                        #self.ext,
                        #self.cache_dir,
                        #self.options)

