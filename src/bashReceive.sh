#!/bin/sh
# This program is executed any time a new SMS is received.
# It forwards received messages to PROGRAM, given him the senders' number
# and the SMS' content.
PROGRAM=/home/lutcheti/webtext/src/handleSMS.py # TODO: config auto

for i in `seq $SMS_MESSAGES` ; do
    eval "$PROGRAM \"\${SMS_${i}_NUMBER}\" \"\${SMS_${i}_TEXT}\"" >/dev/null 2>&1
done