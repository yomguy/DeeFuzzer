#!/bin/sh
# needs epydoc

dir=/home/momo/dev/deefuzzer/doc/

epydoc -n deefuzzer -u https://github.com/yomguy/DeeFuzzer -o $dir deefuzzer/
rsync -a $dir doc.parisson.com:/var/www/files/doc/deefuzzer/

