#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Guillaume Pellerin

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


import sys
from deefuzzer.tools.xmltodict import *


class XML2Various(object):

    def __init__(self, xml_str):
        self.dict = xmltodict(xml_str, 'utf-8')

    def to_yaml(self):
        import yaml
        return yaml.dump(self.dict)


if __name__ == '__main__':
    xml_file = open(sys.argv[-2], 'r')
    yaml_file = open(sys.argv[-1], 'w')
    yaml_file.write(XML2Various(xml_file.read()).to_yaml())
    xml_file.close()
    yaml_file.close()


