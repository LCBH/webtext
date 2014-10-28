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
fast. We call it the "request server". The request server parse the request, fetch the
required information and format it into a SMS' text. Finally, either it sends
this text using a carrier API or it sends back to the rasp which then sends the SMS.

Sol for 2:  we cannot fully rely on weboob. We thus need a modular code that uses
either weboob or soem external APIs.


## Architecture:
- code for the rasp in src/rasp on rasp branch
- code for the request server in src/request on request branch
Install scripts in ./