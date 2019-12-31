#!/usr/bin/env python
# -*- coding: utf-8 -*-

import liblo
import sys

# send all messages to port 1234 on the local machine
try:
    target = liblo.Address(1234)
except liblo.AddressError as err:
    print(str(err))
    sys.exit()

# send message "/foo/message1" with int, float and string arguments
liblo.send(target, "/twitter", 1)
