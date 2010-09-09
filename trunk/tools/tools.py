#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2007-2009 Guillaume Pellerin <yomguy@parisson.com>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution. The terms
# are also available at http://svn.parisson.org/deefuzz/wiki/DefuzzLicense.
#
# Author: Guillaume Pellerin <yomguy@parisson.com>

import os
import re
import string

def clean_word(word) :
    """ Return the word without excessive blank spaces, underscores and
    characters causing problem to exporters"""
    word = re.sub("^[^\w]+","",word)    #trim the beginning
    word = re.sub("[^\w]+$","",word)    #trim the end
    word = re.sub("_+","_",word)        #squeeze continuous _ to one _
    word = re.sub("^[^\w]+","",word)    #trim the beginning _
    #word = string.replace(word,' ','_')
    #word = string.capitalize(word)
    dict = '&[];"*:,'
    for letter in dict:
        word = string.replace(word,letter,'_')
    return word

def get_file_info(media):
    file_name = media.split(os.sep)[-1]
    file_title = file_name.split('.')[:-1]
    file_title = '.'.join(file_title)
    file_ext = file_name.split('.')[-1]
    return file_name, file_title, file_ext
