#!/bin/bash

conf_file=$1
log_file=/tmp/deefuzz.log

set -e
ulimit -c unlimited
while true; do
  deefuzz $1 > /dev/null
  sleep 3
done
