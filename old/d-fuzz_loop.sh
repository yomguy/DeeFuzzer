#!/bin/sh
ulimit -c unlimited
while true; do
ezstream -c $1.xml > /dev/null;
sleep 3
done
