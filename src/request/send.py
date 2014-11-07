# -- coding: utf-8 --
###########################################################################
#                                                                         #
#                       WebText                                           #
#                                                                         #
#                       Lucca Hirschi                                     #
#                       <lucca.hirschi@ens-lyon.fr>                       #
#                                                                         #
#    Copyright 2014 Lucca Hirschi                                         #
#                                                                         #
#    This file is part of OwnShare.                                       #
#    OwnShare is free software: you can redistribute it and/or modify     #
#    it under the terms of the GNU General Public License as published by #
#    the Free Software Foundation, either version 3 of the License, or    #
#    (at your option) any later version.                                  #
#                                                                         #
#    OwnShare is distributed in the hope that it will be useful,          #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of       #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the        #
#    GNU General Public License for more details.                         #
#                                                                         #
#    You should have received a copy of the GNU General Public License    #
#    along with OwnShare.  If not, see <http://www.gnu.org/licenses/>.    #
#                                                                         #
###########################################################################

""" Using either carrier API's or the raspberry pi, we define functions
that send SMSs."""

import os
import sys
import wget                     # wget command (for api free)
import urllib                   # used to transform text into url
import logging
from os.path import expanduser

# -- Static data (install). --
REQUEST_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(REQUEST_DIR) + "/../"
LOG_DIR = PROJECT_DIR + "data/log/"
# -- User Data --
#if os.path.isfile(PROJECT_DIR+'config_backends.txt'):
execfile(expanduser(PROJECT_DIR+'config_backends.py'))
# -- Setup Logging ''
logging.basicConfig(filename=LOG_DIR + 'handleSMS.log',
                    level=logging.DEBUG,
                    format='%(asctime)s|%(levelname)s|send:%(message)s',
                    datefmt='%d/%m %I:%M:%S %p')

# -- functions --
def sendTextFree(text, login, password):
    """ Send the message [text] through the Free API
    (so only to the corresponding nb.)."""
    logging.info("Sending using FREE API....")
    encodedText = urllib.quote_plus(text) # url-ize the message's content
    url = ('https://smsapi.free-mobile.fr/sendmsg?user=%s&pass=%s&msg=%s'
           % (login, password, encodedText))
    filename = "./tmp/torm.tmp"
    # TOOD: do not wget when testing (see tests.py)
    out = wget.download(url,out=filename)
    os.remove(filename)

def sendText(text, user):
    """ Send the message [text]."""
    logging.info("Starting sendTextFREE.")
    userSend = user['sendSMS']
    if userSend['method'] == "FREE_API":
        sendTextFree(text, userSend['login'], userSend['password'])
    else:
        logging.info("Sending capabiility is not defined for user %s." % (user['login']))
        
        
