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
if __name__ == "__main__":
    # if this is executed as a script: logging using stdout
    logging.basicConfig(stream = sys.stdout,
                        level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(name)s:  %(message)s',
                        datefmt='%H:%M:%S')
else:
    # otherwise, we are testing using test.py -> use its logger
    logging = logging.getLogger(__name__)

# -- Static data (install). --
REQUEST_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(REQUEST_DIR) + "/../../"
LOG_DIR = PROJECT_DIR + "data/log/"
execfile(expanduser(PROJECT_DIR+'config_backends.py'))
conf_database = CONF['config_database']

def testUtils():
    logging.info("## Read Config ##")
    utils.readConfig()
    
    logging.info("\n## Test printInfo(): ")
    utils.printInfo()
    
    logging.info("\n## Test db.py: ")
    # # WARNING:
    # dB = utils.connect()
    # table = dB['store']
    # table.delete()


    logging.info("\n" + "#"*20 + " MULTIPLE MESSAGES " + 20*"#")
    logging.info("CLEAR...")
    dat.clearQueue({'login' : 'lutcheti'})
    logging.info("PUSH...")
    dat.pushMessage({'login' : 'lutcheti'}, ["[1/2] COUCOU", "[2/2] RECOUCOU"])
    dat.pushMessage({'login' : 'lutcheti'}, ["[1/2] AHAH", "[2/2] REAHAHAH"])
    logging.info("POP: ")
    logging.info(dat.popMessage({'login' : 'lutcheti'}))
    
    nT = "0632368092"
    logging.info("\n" + "#"*20 + " ANONYMS " + 20*"#")
    logging.info("Clear Table..")
    dat.clearAno()
    logging.info("Add Anonyms %s" % (str(nT)))
    dat.addAno(nT)
    logging.info("A 3 requests...")
    dat.addRequest(nT)
    dat.addRequest(nT)
    dat.addRequest(nT)
    logging.info("hasReached?: ")
    logging.info(dat.hasReachedLimit(nT))
    logging.info("Add 20 more requests.")
    for i in range(20):
        dat.addRequest(nT)
    logging.info("hasReached?: ")
    logging.info(dat.hasReachedLimit(nT))


    logging.info("\n" + "#"*20 + " YELP IDs businesses " + 20*"#")
    # logging.info("CLEAR...")
    # dat.clearYelpIDs({'login' : 'lutcheti'})
    logging.info("STORE...")
    dat.storeYelpIDs({'login' : 'lutcheti'},
                    [{'id' : "lolive12", "name": "L'olive",
                      'rating' : 4, 'location' : {'display_address': "12, rue Riquet, Paris"}},
                     {'id' : "en-vrac3", "name": "En Vrac",
                      'rating' : 5, 'location' : {'display_address': "2, rue Riquet, Paris"}}
                     ])
    logging.info("GET...")
    logging.info(str(dat.getYelpIDs({'login' : 'lutcheti'}, number=3)))

    logging.info("\n" + "#"*20 + " Exporting Json and print " + 20*"#")
    logging.info(" Users:")
    logging.info(utils.exportJson(tableName='users'))
    logging.info(" SendSMS:")
    logging.info(utils.exportJson(tableName='sendSMS'))
    logging.info(" Shortcuts:")
    logging.info(utils.exportJson(tableName='shortcuts'))
    logging.info(" Backends:")
    logging.info(utils.exportJson(tableName='backends'))
    logging.info(" Store:")
    logging.info(utils.exportJson(tableName='store'))
    logging.info(" YelpIDs:")
    logging.info(utils.exportJson(tableName='yelpIDs'))
    logging.info(" Anonym:")
    logging.info(utils.exportJson(tableName='anonym'))

testUtils()

# LIB:
# https://dataset.readthedocs.org/en/latest/quickstart.html
