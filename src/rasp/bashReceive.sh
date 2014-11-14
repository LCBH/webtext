#!/bin/bash
# This program is executed any time a new SMS is received.
# It forwards received messages to handleSMS (for requests that needs private data)
# given him the senders' number and the SMS' content AND sends the request through HTTP
# to the request server as well.
echo Starting screen of bashReceive:
PROGRAM=/home/lutcheti/webtext/src/request/handleSMS.py # TODO: config auto
source /home/lutcheti/webtext/config_rasp.cfg
for i in `seq $SMS_MESSAGES` ; do
    echo "screen -S parseAndSend -d -m python $PROGRAM \"\${SMS_${i}_NUMBER}\" \"\${SMS_${i}_TEXT}\" \"false\" \"true\" &"
    eval "screen -S parseAndSend -d -m python $PROGRAM \"\${SMS_${i}_NUMBER}\" \"\${SMS_${i}_TEXT}\" \"false\" \"true\" &"
    # We need to URLEncode SMS'content before using curl
    ESCAPED_TEXT="$(perl -MURI::Escape -e 'print uri_escape($ARGV[0]);' "${SMS_1_TEXT}")"
    curl -k "https://www.choum.net/webtext/api/sms.php?pass=${API_SECRET_KEY}&numero=${SMS_1_NUMBER}&content=${ESCAPED_TEXT}&isTesting=false"
done
echo Ending screen of bashReceive.