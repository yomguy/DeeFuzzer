#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
from threading import Thread


class Logger:
    """A logging object"""

    def __init__(self, file):
        self.logger = logging.getLogger('myapp')
        self.hdlr = logging.FileHandler(file)
        self.formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        self.hdlr.setFormatter(self.formatter)
        self.logger.addHandler(self.hdlr)
        self.logger.setLevel(logging.INFO)

    def write_info(self, message):
        self.logger.info(message)

    def write_error(self, message):
        self.logger.error(message)

class QueueLogger(Thread):
    """A queue-based logging object"""
    
    def __init__(self, file, q):
        Thread.__init__(self)
        self.logger = Logger(file)
        self.q = q
        
    def run(self):
        while True:
            try:
                msg = self.q.get(1)
                if not isinstance(msg, dict):
                    self.logger.write_error(str(msg))
                else:
                    if not 'msg' in msg.keys():
                        continue
                    
                    if 'level' in msg.keys():
                        if msg['level'] == 'info':
                            self.logger.write_info(msg['msg'])
                        else:
                            self.logger.write_error(msg['msg'])
                    else:
                         self.logger.write_error(msg['msg'])
            except:
                pass
                