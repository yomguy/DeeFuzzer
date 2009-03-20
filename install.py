#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2006-2007 Guillaume Pellerin <yomguy@altern.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA

# ONLY FOR LINUX / UNIX

import os, sys

if len(sys.argv) == 1:
    install_dir = '/usr/share/deefuzz/'
elif len(sys.argv) > 2:
    sys.exit('Give just one directory to install Telemeta, or none.')
else:
    install_dir = sys.argv[1]

if not os.path.exists(install_dir):
    os.mkdir(install_dir)

os.system('cp -ra ./* '+install_dir+os.sep)
os.system('rm -rf '+install_dir+os.sep+'debian')

if os.path.exists('/usr/bin/deefuzz'):
    os.system('rm -r /usr/bin/deefuzz')

os.system('ln -s '+install_dir+os.sep+'deefuzz.py '+'/usr/bin/deefuzz')

print """
   Installation successfull ! 
   Type 'deefuzz' now...
   """

