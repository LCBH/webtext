#!/usr/bin/python
# -*- coding: utf-8 -*-
# This program is executed any time a new SMS is received.
# argv[1] contains the senders' number and argv[2] contains the content of
# the SMS

import os
import sys
import wget                     # wget command (for api free)
import subprocess               # for launching bash programs
import urllib                   # used to transform text into url
import logging

# Those constants must be imported from a config file (todo)
FREE_USER = "92327715"
FREE_PASSWD = "uKNH3j5xEtjmtg"

SMSnumber = sys.argv[1]
SMScontent = sys.argv[2]

# Setup Logging
logging.basicConfig(filename='/home/lutcheti/webtext/data/log/handleSMS.log',
                    level=logging.DEBUG,
                    format='%(asctime)s|%(levelname)s|%(name)s:%(message)s',
                    datefmt='%d/%m %I:%M:%S %p')
logging.info("Starting handleSMS.py with number:[%s] and content:[%s]." % (SMSnumber,SMScontent))

# send the message text through the Free API (so only to the corresponding nb.)
def sendText(text):
    logging.info("Starting sendText")
    encodedText = urllib.quote_plus(text)
    url = ('https://smsapi.free-mobile.fr/sendmsg?user=%s&pass=%s&msg=%s'
           % (FREE_USER, FREE_PASSWD, encodedText))
    filename = "./tmp/torm.tmp"
    out = wget.download(url,out=filename)
    os.remove(filename)

# Parse the inputted text and output the corresponding answer
def parseContent(text):
    logging.info("Starting parseContent")
    if text == "banque":
        return(bankInfo())
    elif text == "banque details":
        return(bankInfo(True))
    elif text[:4] == "velo":
        if text == "velo":
            where = "chapelle"
        elif text == "velo moi":
            where = "riquet"
        else:
            where = text[5:]
        velibParis(where)
    else:
        extract = ('Le numéro %s ma envoyé le texte %s' % (SMSnumber, SMScontent))
        answer = ("Bonjour, je suis la Raspberry Pi et j'ai un problème. " +
                  extract +
                  ", malheuresement je n'ai pas compris sa requête.")
        return(answer)

def bankInfo(details=False):
    logging.info("Starting bankInfo")
    bashCommandList = "boobank list --formatter=multiline --select=label,balance"
    bashCommandHistory = ("boobank history 102780735700020237601EUR@creditmutuel "
                          "--formatter=multiline --select=date,raw,amount")
    logging.info("Before subprocess: %s" % bashCommandList)
    process = subprocess.Popen(bashCommandList.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]
    if details:
        logging.info("More details needed, before subprocess: %s" % bashCommandHistory)
        process = subprocess.Popen(bashCommandHistory.split(), stdout=subprocess.PIPE)
        outputHistory = process.communicate()[0]
        output = output + "||| Les détails:\n" + str(outputHistory)
    answer = ("J'ai compris que tu voulais un point sur tes comptes:\n" +
              str(output))
    return(answer)

def velibParis(where):
    logging.info("Starting velibParis")
    bashPrefix = "boobsize search --formatter=multiline "
    bashPrefix2 = "boobsize last_sensor_measure "
    # prefixBikes = "available_bikes"
    # prefixFree = "available_bike_stands"
    # stationChap = ".18040.Paris.jcvelaux"
    # stationDep = "18110.Paris.jcvelaux"
    # stationRiqet = ".18010.Paris.jcvelaux"
    # stationRiquetP = ".18109.Paris.jcvelaux"
    if where == "chapelle":
#        bashC =  bashPrefix2 + prefixBikes + stationChap
        bashC = bashPrefix + "marx dormoy"
    elif where == "moi":
        bashC = bashPrefix + "riquet"
    else:
        bashC = bashPrefix + where
    logging.info("Before subprocess: %s." % bashC)
    process = subprocess.Popen(bashC.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]
#     output = output[0:200]      # TO FIX
    answer = ("J'ai compris que tu voulais avoir les dispos des vélos à "+where+"."
              " Voici ces infos:\n" +
              str(output))
    return(answer)

answer = parseContent(SMScontent)
logging.info("Answer is: " + answer)
sendText(answer)
logging.info("Sent OK, END of handleSMS")
