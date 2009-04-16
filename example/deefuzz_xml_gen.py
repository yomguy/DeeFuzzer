#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from string import Template

nb_station = sys.argv[1]
deefuzz_from = sys.argv[2]
deefuzz_to = sys.argv[3]

df = open(deefuzz_from, 'r')
dt = open(deefuzz_to, 'w')
t = Template(df.read())

dt.write('<deefuzz>\n')
dt.write('    <log>/tmp/deefuzz.log</log>\n')
dt.write('    <m3u>/tmp/deefuzz.m3u</m3u>\n')

for i in range(0,int(nb_station)):
    xml = t.substitute(number='_'+str(i+1))
    dt.write(xml)
dt.write('</deefuzz>\n')

df.close()
dt.close()
