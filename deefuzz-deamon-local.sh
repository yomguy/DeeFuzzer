#!/bin/bash

conf_file=$1
log_file=/tmp/deefuzz.log

set -e
ulimit -c unlimited
while true; do
  ./deefuzz.py $1
  sleep 3
done
