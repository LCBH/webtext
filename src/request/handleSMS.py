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

# This program is executed any time a new SMS is received or a HTTP request.
# arguments: number, SMS' content, is_testing, run_is_local, ?password 
# booleans are given as strings
# if is_testing == "true", we do not send the answer by SMS
from __future__ import unicode_literals # implicitly declaring all strings as unicode strings

import os
import sys
import wget                     # wget command (for api free)
import subprocess               # for launching bash programs
import urllib                   # used to transform text into url
import logging
from os.path import expanduser

import parse
import send


# -- Static data (install). --
REQUEST_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(REQUEST_DIR) + "/../"
LOG_DIR = PROJECT_DIR + "data/log/"
execfile(expanduser(PROJECT_DIR+'config_backends.py'))

# -- Setup Logging --
if __name__ == "__main__":
    # if this is executed as a script: logging in a file
    logging.basicConfig(filename=LOG_DIR + 'handleSMS.log',
                        level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(name)s:  %(message)s',
                        datefmt='%d/%m %H:%M:%S')
else:
    # otherwise, we are testing using test.py -> use sdout
    logger = logging.getLogger(__name__)


# -- Helping functions --
def ofb(s):
    return(s=="true")

def searchUser(dic, number):
    """ Given a configuration file (config_backends.py) and a number,
    search for the corresponding user's config."""
    number=(str(number))
    if number[0] == " ":
        # Means that it was a '+' but it has been URLencoded
        number = "+" + number[1:]
    matches = [u for u in dic['users'] if u['number']==number]
    if matches != []:
        return matches[0]

# -- START MAIN --
def main(is_testing, is_local, content, number, password=""):
    logging.info("--------------------------------------------------------------\n"
                 "--- Starting handleSMS.py with number:[%s] and content:[%s]. ---"
                 % (number,content))        
    # Check the password if not executed locally
    api_secret_key = CONF['config_api']['api_secret_key']
    if not(is_local) and password != api_secret_key:
        logging.warning("ERROR SECRET_KEY_API! (try with: %s)." % password)
        return None

    user = searchUser(CONF, number)
    if user == None:    
        logging.warning("I will not process the request since the sender is not in the white list")
    else:
        logging.info("The SMS comes from the user %s (name: %s)." % (user['login'], user['name']))
        # extract config of banckends
        config_backends = CONF['config_backends']
        answers, optionsDict = parse.produceAnswers(content, user, config_backends, is_local=is_local, is_testing=is_testing)
        if answers != None and answers != []:
            logging.info("Answer is: " + '|| '.join(answers))
            send.sendText(answers, user, optionsDict, is_testing=is_testing)
            logging.info("END of handleSMS")
        else:
            logging.info("Pas de réponse! (privée + distant?).")

# If this is executed as a script, we parse argv
if __name__ == "__main__":
    # arguments: number, SMS' content, is_testing, run_is_local, ?password 
    SMSnumber = sys.argv[1]
    SMScontent = sys.argv[2]
    IS_TESTING = sys.argv[3]
    IS_LOCAL = sys.argv[4]          # true if launch from rasp and false otherwise
    if not(ofb(IS_LOCAL)):
        # in tha that case the api's secret key a password is required
        PASSWORD = sys.argv[5]
        main(is_testing=ofb(IS_TESTING), is_local=False, content=SMScontent, number=SMSnumber, password=PASSWORD)
    else:
        main(is_testing=ofb(IS_TESTING), is_local=True, content=SMScontent, number=SMSnumber)
