#!/usr/bin/python

import sys, os, random

def randrange(start, stop):
	values = range(start, stop)
	random.shuffle(values)
	while values:
		yield values.pop()
	raise StopIteration



