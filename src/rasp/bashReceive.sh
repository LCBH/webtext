#!/bin/bash
# This program is executed any time a new SMS is received.
# It forwards received messages to PROGRAM, given him the senders' number
# and the SMS' content.
echo Starting screen of bashReceive:
PROGRAM=/home/lutcheti/webtext/src/request/handleSMS.py # TODO: config auto
API_KEY=bhk126T74IY5sdfBNdfg35
for i in `seq $SMS_MESSAGES` ; do
    echo "screen -S parseAndSend -d -m python $PROGRAM \"\${SMS_${i}_NUMBER}\" \"\${SMS_${i}_TEXT}\" \"false\" \"true\" &"
    eval "screen -S parseAndSend -d -m python $PROGRAM \"\${SMS_${i}_NUMBER}\" \"\${SMS_${i}_TEXT}\" \"false\" \"true\" &"
    echo "curl -X 'https://www.choum.net/webtext/api/sms.php?pass=$API_KEY&numero=\${SMS_${i}_NUMBER}&content=\${SMS_${i}_TEXT}\'"
    eval "curl -X 'https://www.choum.net/webtext/api/sms.php?pass=$API_KEY&numero=\${SMS_${i}_NUMBER}&content=\${SMS_${i}_TEXT}\'"
done
echo Ending screen of bashReceive.

# TODO: From now, on: raspberry sends (number,SMS) to the "request server"
# replace here the call of handleSMS.py by a wget request
# to it using Python and log everything locally