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

# Those constants must be imported from a config file (todo)
FREE_USER = HIDDEN
FREE_PASSWD = HIDDEN

SMSnumber = sys.argv[1]
SMScontent = sys.argv[2]

# send the message text through the Free API (so only to the corresponding nb.)
def sendText(text):
    encodedText = urllib.quote_plus(text)
    url = ('https://smsapi.free-mobile.fr/sendmsg?user=%s&pass=%s&msg=%s'
           % (FREE_USER, FREE_PASSWD, encodedText))
    filename = "./tmp/torm.tmp"
    out = wget.download(url,out=filename)
    os.remove(filename)

# Parse the inputted text and output the corresponding answer
def parseContent(text):
    if text == "banque":
        return(bankInfo())
    elif text == "banque details":
        return(bankInfo(True))
    else:
        extract = ('Le numéro %s ma envoyé le texte %s' % (SMSnumber, SMScontent))
        answer = ("Bonjour, je suis la Raspberry Pi et j'ai un problème. " +
                  extract +
                  ", malheuresement je n'ai pas compris sa requête.")
        return(answer)

def bankInfo(details=False):
    bashCommandList = "boobank list --formatter=multiline --select=label,balance"
    bashCommandHistory = ("boobank history 102780735700020237601EUR@creditmutuel "
                          "--formatter=multiline --select=date,raw,amount")
    process = subprocess.Popen(bashCommandList.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]
    if details:
        process = subprocess.Popen(bashCommandHistory.split(), stdout=subprocess.PIPE)
        outputHistory = process.communicate()[0]
        ourput = output + "||| Les détails:\n" + str(outputHistory)
    answer = ("J'ai compris que tu voulais un point sur tes comptes:\n" +
              str(output))
    return(answer)


answer = parseContent(SMScontent)
print("Voici la réponse:\n" + answer)
sendText(answer)
