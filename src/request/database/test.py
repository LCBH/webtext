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

""" Some tests for database/utils.py and database/db.py. """
from __future__ import unicode_literals # implicitly declaring all strings as unicode strings

import os
import sys
import wget        
import subprocess  
from os.path import expanduser
import datetime
import json
import logging

import db as dat
import utils

# -- Setup Logging --
logging.basicConfig(stream = sys.stdout,
                    level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(name)s:  %(message)s',
                    datefmt='%H:%M:%S')

# -- Static data (install). --
REQUEST_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(REQUEST_DIR) + "/../../"
LOG_DIR = PROJECT_DIR + "data/log/"
execfile(expanduser(PROJECT_DIR+'config_backends.py'))
conf_database = CONF['config_database']

def testUtils():
    print("## Read Config ##")
    utils.readConfig()
    
    print("\n## Test printInfo(): ")
    utils.printInfo()
    
    print("\n## Test db.py: ")
    # WARNING:
    dB = utils.connect()
    table = dB['store']
    table.delete()

    print("CLEAR...")
    dat.clearQueue({'login' : 'lutcheti'})
    print("PUSH...")
    dat.pushMessage({'login' : 'lutcheti'}, ["[1/2] COUCOU", "[2/2] RECOUCOU"])
    dat.pushMessage({'login' : 'lutcheti'}, ["[1/2] AHAH", "[2/2] REAHAHAH"])
    print("POP: ")
    print(dat.popMessage({'login' : 'lutcheti'}))

    print("\n## Exporting Json and print ##")
    print(" Users:")
    print(utils.exportJson(tableName='users'))
    print(" SendSMS:")
    print(utils.exportJson(tableName='sendSMS'))
    print(" Shortcuts:")
    print(utils.exportJson(tableName='shortcuts'))
    print(" Backends:")
    print(utils.exportJson(tableName='backends'))
    print(" Store:")
    print(utils.exportJson(tableName='store'))

testUtils()

# LIB:
# https://dataset.readthedocs.org/en/latest/quickstart.html
