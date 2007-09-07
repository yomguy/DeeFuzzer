#!/usr/bin/python

import sys, os, random

#Playdir='/home/cellar/Cellar_playlist/'
#IndexFile='/home/cellar/stream/d-fuzz_1_index.txt'
#RandomIndexListFile='/home/cellar/stream/d-fuzz_1_random_index_list.txt'
#PlaylistLengthOrigFile='/home/cellar/stream/d-fuzz_1_playlist_length.txt'

def randrange(start, stop):
	values = range(start, stop)
	random.shuffle(values)
	while values:
		yield values.pop()
	raise StopIteration



