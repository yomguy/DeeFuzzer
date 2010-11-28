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

# ONLY FOR LINUX / UNIX

import os, sys
import platform

if len(sys.argv) == 1:
    install_dir = '/usr/share/deefuzzer/'
elif len(sys.argv) > 2:
    sys.exit('Give just one directory to install the DeeFuzzer, or none.')
else:
    install_dir = sys.argv[1]

if not os.path.exists(install_dir):
    os.mkdir(install_dir)

os.system('cp -ra ./* '+install_dir+os.sep)

# Install shout-python
os.chdir('shout-python')
os.system('python setup.py install')
os.chdir('..')

os.system('easy_install tinyurl')

if os.path.exists('/usr/bin/deefuzzer'):
    os.system('rm -r /usr/bin/deefuzzer')

os.system('ln -s '+install_dir+os.sep+'deefuzzer.py '+'/usr/bin/deefuzzer')

print """
   DeeFuzzer installation successfull !
   """

