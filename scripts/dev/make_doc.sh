#!/bin/sh
# needs epydoc

app="deefuzzer"
dir=/home/$USER/dev/$app/doc/
server="doc.parisson.com"

epydoc -n $app -u https://github.com/yomguy/DeeFuzzer -o $dir $app/
rsync -a $dir $server:/var/www/files/doc/$app/

