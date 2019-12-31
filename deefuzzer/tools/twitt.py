#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2006-2009 Guillaume Pellerin

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


# Twitter DeeFuzzer keys
DEEFUZZER_CONSUMER_KEY = 'ozs9cPS2ci6eYQzzMSTb4g'
DEEFUZZER_CONSUMER_SECRET = '1kNEffHgGSXO2gMNTr8HRum5s2ofx3VQnJyfd0es'


class Twitter:
    def __init__(self, key, secret):
        import twitter

        self.consumer_key = DEEFUZZER_CONSUMER_KEY
        self.consumer_secret = DEEFUZZER_CONSUMER_SECRET
        self.access_token_key = key
        self.access_token_secret = secret
        self.api = twitter.Api(consumer_key=self.consumer_key,
                               consumer_secret=self.consumer_secret,
                               access_token_key=self.access_token_key,
                               access_token_secret=self.access_token_secret)

    def post(self, message):
        try:
            self.api.PostUpdate(message)
        except:
            pass

