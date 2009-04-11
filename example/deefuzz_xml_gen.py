#!/usr/bin/python

import sys
from string import Template

nb_station = sys.argv[1]
deefuzz_from = sys.argv[2]
deefuzz_to = sys.argv[3]

df = open(deefuzz_from, 'r')
dt = open(deefuzz_to, 'w')
t = Template(df.read())

dt.write('<deefuzz>\n')
for i in range(0,int(nb_station)):
    xml = t.substitute(station='MyDeeFuzz_'+str(i+1))
    dt.write(xml)
dt.write('</deefuzz>\n')

df.close()
dt.close()
