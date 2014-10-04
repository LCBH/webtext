webtext
=======

*Web for old phones through a Raspberry Pi*

## Goals
**Task1**: I text to my Raspberry some question,
I receive its answer within a minute.

Some examples:
- "train next departure StationA" -> "request received at 13h45: next departure from StationA at 14h15, following one at 15h45"
- "bikes Railway Station" -> "request received at 17h46: there is 6 bikes left and 5 free slots at the bike station next to the railway station"
- "train from Paris to Marseille 13th March -> list of trains and prices
- "bank amount [passphrase]" -> amounts of your bank accounts
- "forecast Marseille 14th March" -> precise forecast
- "Gmail subjects list" -> list of (id,subject of id's email)
- "Gmail body 3" -> body of email whose id=3


**Task2**: I let a voicemail on my raspberry's number with my request, it answers me by SMS.


## Tech
**Hardware**: a Sim Card reader, a Sim Card with a 0euro phone plan (e.g., Prixtel in France) only used to receive SMSs, a raspberry Pi.
In order to send free SMSs, we use a common feature of most of mobile operators: by sending an email
to [phone number]@[mobile operator website], the email is forwarded by SMS to [phone number].

**Software**: project [Weboob](http://weboob.org/) (scriptable routines for fetching info from websites), Python and Google scripts to glue everything together.


## Roadmap
1. Task1, focus on train and bikes, interacting with the raspberry pi by letting a voicemail (0 or 1)
2. 1. + interacting using SMSs
3. Task2
