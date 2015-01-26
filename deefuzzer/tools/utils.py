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
import mimetypes
from itertools import chain
from deefuzzer.tools import *

mimetypes.add_type('application/x-yaml', '.yaml')


def clean_word(word):
    """ Return the word without excessive blank spaces, underscores and
    characters causing problem to exporters"""
    word = re.sub("^[^\w]+", "", word)  # trim the beginning
    word = re.sub("[^\w]+$", "", word)  # trim the end
    word = re.sub("_+", "_", word)  # squeeze continuous _ to one _
    word = re.sub("^[^\w]+", "", word)  # trim the beginning _
    # word = string.replace(word,' ','_')
    # word = string.capitalize(word)
    dict = '&[];"*:,'
    for letter in dict:
        word = string.replace(word, letter, '_')
    return word


def get_file_info(media):
    file_name = media.split(os.sep)[-1]
    file_title = file_name.split('.')[:-1]
    file_title = '.'.join(file_title)
    file_ext = file_name.split('.')[-1]
    return file_name, file_title, file_ext


def is_absolute_path(path):
    return os.sep == path[0]


def merge_defaults(setting, default):
    combined = {}
    for key in set(chain(setting, default)):
        if key in setting:
            if key in default:
                if isinstance(setting[key], dict) and isinstance(default[key], dict):
                    combined[key] = merge_defaults(setting[key], default[key])
                else:
                    combined[key] = setting[key]
            else:
                combined[key] = setting[key]
        else:
            combined[key] = default[key]
    return combined


def replace_all(option, repl):
    if isinstance(option, list):
        r = []
        for i in option:
            r.append(replace_all(i, repl))
        return r
    elif isinstance(option, dict):
        r = {}
        for key in option.keys():
            r[key] = replace_all(option[key], repl)
        return r
    elif isinstance(option, str):
        r = option
        for key in repl.keys():
            r = r.replace('[' + key + ']', repl[key])
        return r
    return option


def get_conf_dict(file):
    mime_type = mimetypes.guess_type(file)[0]

    # Do the type check first, so we don't load huge files that won't be used
    if 'xml' in mime_type:
        confile = open(file, 'r')
        data = confile.read()
        confile.close()
        return xmltodict(data, 'utf-8')
    elif 'yaml' in mime_type:
        import yaml

        def custom_str_constructor(loader, node):
            return loader.construct_scalar(node).encode('utf-8')

        yaml.add_constructor(u'tag:yaml.org,2002:str', custom_str_constructor)
        confile = open(file, 'r')
        data = confile.read()
        confile.close()
        return yaml.load(data)
    elif 'json' in mime_type:
        import json

        confile = open(file, 'r')
        data = confile.read()
        confile.close()
        return json.loads(data)

    return False


def folder_contains_music(folder):
    files = os.listdir(folder)
    for file in files:
        filepath = os.path.join(folder, file)
        if os.path.isfile(filepath):
            mime_type = mimetypes.guess_type(filepath)[0]
            if 'audio/mpeg' in mime_type or 'audio/ogg' in mime_type:
                return True
    return False
