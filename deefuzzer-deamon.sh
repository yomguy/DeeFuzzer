#!/bin/bash

conf_file=$1
log_file=/tmp/deefuzzer.log

set -e
ulimit -c unlimited
while true; do
  deefuzzer $1 > /dev/null
  sleep 3
done
