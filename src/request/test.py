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

""" Tests all the scripts."""

import os
import sys
from os.path import expanduser
import logging
import pprint
from sys import stdin

import handleSMS
import database
import send
from backends.main import Backend

# -- Static data (install). --
REQUEST_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(REQUEST_DIR) + "/../"
# -- User Data --
# if os.path.isfile(PROJECT_DIR+'config_backends.py'):
execfile(expanduser(PROJECT_DIR+'config_backends.py'))

logging.basicConfig(stream = sys.stdout,
# If you want to only display errors and warnings;
#                   level=logging.WARNING,
                    level=logging.DEBUG,
#                    level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(name)s:  %(message)s',
                    datefmt='%H:%M:%S')

pp = pprint.PrettyPrinter(indent=4)

user1 = [ u for u in CONF['users'] if u['login'] == 'luccaH'][0]
user2 = [ u for u in CONF['users'] if u['login'] == 'vincentCA'][0]

def callHandle(content,number):
    return(handleSMS.main(is_testing=True,is_local=True, content=content, number=number))


testSystem = True
testDatabase = True
testBackend = True
testInteractive = False
testSend = False
theBackend = None
notAdmin = False

if len(sys.argv) > 1:
    if sys.argv[1] == "backends": # test all backends
        testSystem = False
        testDatabase = False
    if sys.argv[1] == "backend": # test only the backend [argv[2]]
        testSystem = False
        testDatabase = False
        theBackend = sys.argv[2]
    if sys.argv[1] == "backendsNotAdmin": # test all backends except admin
        testSystem = False
        testDatabase = False
        notAdmin = True
    if sys.argv[1] == "system": # test only the core system
        testBackend = False
        testDatabase = False
    if sys.argv[1] == "i":      # interative mode
        testInteractive = True
    if sys.argv[1] == "send":
        testSend = True
        testBackend = False
        testDatabase = False
        testSystem = False

if testInteractive:
    userinput = None
    while (userinput != "q"):
        print("Type a request...\n")
        userinput = stdin.readline()
        print("We are going to process the following request: %s." % userinput)
        callHandle(str(userinput), user1['number'])
        print("Done. (type 'q' to quit)")

if testSystem:
    logging.info("\n" + "=" * 40 + "  TESTING the whole system on serveral requests  " + 40 * "=")
    # This is important to check the parsing of plain text requests, shortcuts handling etc.
    # TODO: check the output of those commands
    callHandle("Coucou", user1['number'])
    callHandle("aide; trafic", user1['number'])
    callHandle("aide; wiki", user1['number'])
    callHandle("trafic", user1['number'])
    callHandle("cine louxor", user2['number'])
    callHandle("meteo 75020", user1['number'])
    callHandle("aide; trafic", " 33632368092")
    callHandle("trafic", " 33632368093")
    # callHandle("retour", user1['number'])
    # callHandle("wiki github", user1['number'])
    # callHandle("velo marx dormoy", user1['number'])
    # callHandle("cine birdman 75000", user2['number'])        

if testDatabase:    
    logging.info("\n\nn" + "=" * 40 + "  TESTING database/  " + 40 * "=")
    import database.test

if testBackend:
    resultsTests = {}
    logging.info("\n\n" + "=" * 40 + "  TESTING backends  " + 40 * "=")
    logging.info("There are %d backends." % sum(1 for _ in Backend))

    # We iterate over all existing backeds and check if backendName matches
    for backend in Backend:
        if ((not(theBackend) or backend.backendName == str(theBackend)) and
            (not(notAdmin) or backend.backendName != "admin")):
            logging.info("\n." + "-" * 5 + (" testing backend '%s' " % backend.name) + "-" * 5)
            notBroken = backend.test(user1)
            notBrokenHelp = backend.help()
            if notBroken and notBrokenHelp != None:
                logging.info("Backend passes all tests.")
                resultsTests[backend.name] = True
            else:
                logging.info("="*5 + "> BROKEN BACKEND <" +"="*5 + "\n")
                resultsTests[str(backend.name)] = False
    pp.pprint("Summary of tests:\n")               
    pp.pprint(resultsTests)

if testSend:
    NB = 999                    # API FREE's limit is at 999
    # NB = 160                    # limit one SMS by Gammu
    # NB = 2001                   # limit multiple SMSs by Gammu (can be bigger)
    # NB = 1750                   # limit multiple SMSs by Gammu - UR'size (max 2000)
    MESS = [str(NB) + "a" * (NB-1-3-1) + "b"]
    send.sendText(MESS, user1, {}, is_testing = False)
