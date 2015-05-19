#!/bin/bash
# This script sends a SMS from the RaspBerry Pi's SIM card
# arg1: number, arg2: api_secre_key, arg3: content
source /home/lutcheti/webtext/config_rasp.cfg
if [ "$2" = "$API_SECRET_KEY" ]
then
  cd /home/lutcheti/webtext/data/SMS/outbox
  sudo gammu-smsd-inject -c /etc/gammu-smsdrc TEXT $1 -len 2001 -textutf8 "$3"
fi