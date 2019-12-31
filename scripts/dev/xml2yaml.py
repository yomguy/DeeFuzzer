#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Guillaume Pellerin

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


