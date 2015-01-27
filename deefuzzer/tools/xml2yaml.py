import os
import sys
import yaml
from deefuzzer.core import DeeFuzzer


path = sys.argv[-1]
d = DeeFuzzer(path)
name, ext = os.path.splitext(path)
y = open(name + '.yaml', 'w')
yaml.dump(d.conf, y)
y.close()
