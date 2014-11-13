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
# arguments: number, SMS' content, is_testing, run_is_local, ?password 
# booleans are given as strings
# is is_testing == "true", we do not send the asnwer by SMS

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
# arguments: number, SMS' content, is_testing, run_is_local, ?password 
SMSnumber = sys.argv[1]
SMScontent = sys.argv[2]
IS_TESTING = sys.argv[3]
IS_LOCAL = sys.argv[4]          # true if launch from rasp and false otherwise
if IS_LOCAL == "false":
    PASSWORD = sys.argv[5]
# -- Static data (install). --
API_SECRET_KEY="bhk126T74IY5sdfBNdfg35"
REQUEST_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(REQUEST_DIR) + "/../"
LOG_DIR = PROJECT_DIR + "data/log/"
# -- User Data --
# if os.path.isfile(PROJECT_DIR+'config_backends.py'):
execfile(expanduser(PROJECT_DIR+'config_backends.py'))
# -- Setup Logging --
logging.basicConfig(filename=LOG_DIR + 'handleSMS.log',
                    level=logging.DEBUG,
                    format='%(asctime)s|%(levelname)s|handle:%(message)s',
                    datefmt='%d/%m %I:%M:%S %p')


def searchUser(dic, number):
    matches = [u for u in dic['users'] if u['number']==(str(number))]
    if matches != []:
        return matches[0]


# -- START MAIN --
def main(is_testing):
    logging.info("Starting handleSMS.py with number:[%s] and content:[%s]." % (SMSnumber,SMScontent))
    # Check the password if not executed locally
    if IS_LOCAL != "false" and PASSWORD != API_SECRET_KEY:
        logging.warning("ERROR SECRET_KEY_API! (try with: %s)." % PASSWORD)
        return None

    if is_testing:
        logging.info("A TEST IS STARTING.")
    user = searchUser(CONF, SMSnumber)
    if user == None:    
        logging.info("I will not process the request since the sender is not in the white list")
    else:
        logging.info("The SMS comes from the user %s (name: %s)." % (user['login'], user['name']))
        answer = parse.parseContent(SMScontent, user)
        logging.info("Answer is: " + answer)
        if not(is_testing):
            send.sendText(answer, user)
            logging.info("Sent OK, END of handleSMS")
    if is_testing:
        logging.info("END OF TEST.")


# When this file executed as a script:
if __name__ == "handeSMS.py":
    if IS_TESTING == "true":
        main(True)
    else:
        main(False)
