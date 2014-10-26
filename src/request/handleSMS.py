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

""" Given a SMS (sender's number, content), we parse here the request, fetch
the result and sends the appropriate answer."""

# OLD: This program is executed any time a new SMS is received.
# argv[1] contains the senders' number and argv[2] contains the content of
# the SMS

########################################
#TODO: 
#  This script will be executed whenever 
# the "request's server" receives a 
# request from the raspberry pi.
# Add a PHP page and adapt the script.
########################################

import os
import sys
import wget                     # wget command (for api free)
import subprocess               # for launching bash programs
import urllib                   # used to transform text into url
import logging
import parse
import fetch
import send
from os.path import expanduser


# -- Inputs: the SMS' number and the SMS' content -- 
SMSnumber = sys.argv[1]         # TODO
SMScontent = sys.argv[2]
# -- Static data (install). --
REQUEST_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(REQUEST_DIR) + "/../"
LOG_DIR = PROJECT_DIR + "data/log/"
# -- User Data --
if os.path.isfile(PROJECT_DIR+'config_backends.txt'):
    execfile(expanduser(PROJECT_DIR+'config_backends.txt'))
# -- Setup Logging --
logging.basicConfig(filename=LOG_DIR + 'handleSMS.log',
                    level=logging.DEBUG,
                    format='%(asctime)s|%(levelname)s|handle:%(message)s',
                    datefmt='%d/%m %I:%M:%S %p')

# -- START MAIN --
logging.info("Starting handleSMS.py with number:[%s] and content:[%s]." % (SMSnumber,SMScontent))
answer = parse.parseContent(SMSnumber, SMScontent)
logging.info("Answer is: " + answer)
send.sendTextFREE(answer)
logging.info("Sent OK, END of handleSMS")
