#!/usr/bin/python
import os
import sys
import wget

# This program is executed any time a new SMS is received.
# argv[1] contains the senders' number and argv[2] contains the content of
# the SMS

FREE_USER = HIDDEN
FREE_PASSWD = HIDDEN

text = ('Number %s have sent text: %s' % (sys.argv[1], sys.argv[2]))
answer = "Regarde comment ca marche bien! Je suis la RaspBerry Pi et voici ma reponse:"
url = ('https://smsapi.free-mobile.fr/sendmsg?user=%s&pass=%s&msg=%s'
       % (FREE_USER, FREE_PASSWD, answer + text))
out = wget.download(url)
