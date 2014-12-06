webtext
=======

*Web for old phones through a Raspberry Pi*

## Goals
**Task1**: I text to my Raspberry some question,
I receive its answer within a minute.
Backends: RATP, Velib, VoyageSNCF, bank, météoFrance, GMail, allocine.

## Problems:
1. for some request, weboob can be VERY slow on a RASP.PI (~ 20 sec) -> do not scale
2. some weboob backends are dead

## Solutions: 
Sol for 1: sends raw request (the SMS's content a second server that must be
fast. We call it the "request server". The request server parses the request, fetch the
required information and format it into a SMS' text. Finally, either it sends
this text using a carrier API or it sends back to the rasp which then sends the SMS.

Sol for 2:  we cannot fully rely on weboob. We thus need a modular code that uses
either weboob or some external APIs.


## Architecture:
# BRANCH RASP: code for the rasp in src/rasp.
bashReceive.sh is executed by Gammu whenever a SMS is received.
This script sends the number+sms' content to:
     - the requested server through a HTTPS request (+secret key API) and;
     - to handleSMS.py as well to process private data (e.g., bank info).
You can test from the raspberry by executing test.sh.

# BRANCH REQUEST: code for the request server in src/request.
sms.php (copy in /var/www) is a piece of PHP that is executed by Apache whenever
a HTTPS packet arrives on choum.net/webtext/API/sms.php. It forwards the
paramaters of the packet to handleSMS.py.
To process the received request, handleSMS.py relies on:
   - parse.py to parse the request (we make some choice on the syntax there);
   - fetch.py to fetch all the needed info and produce an answer;
   - send.py to choose the correct capability to send the answer to the user.
 
   
All the hard work is done in fetch.py. The latter imports backends (one for each
website or API) that may be in src/request/backends).
Everything is logged in the file ./data/log/handleSMS.log.
You should write some tests in test.py and launch all the tests with
"sudo python test.py" (sudo is needed because www-data will also use sudo) and
everything will be printed in stdout instead of the log file.
