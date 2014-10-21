#!/bin/bash
# This program is executed any time a new SMS is received.
# It forwards received messages to PROGRAM, given him the senders' number
# and the SMS' content.
PROGRAM=/home/lutcheti/webtext/src/handleSMS.py # TODO: config auto
for i in `seq $SMS_MESSAGES` ; do
    # TO FIX: syntax for $SMS_{$i}_NUMBER
    screen -A -m -d -S send $PROGRAM $SMS_1_NUMBER $SMS_1_TEXT & # >/dev/null 2>&1
done
