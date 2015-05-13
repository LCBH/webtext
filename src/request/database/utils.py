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

""" Gives a direct access to the database to modifiy, print and freeze it. """
from __future__ import unicode_literals # implicitly declaring all strings as unicode strings

import os
import sys
import wget        
import subprocess  
from os.path import expanduser
import datetime
import json
import logging

import dataset

# -- Setup Logging --
logging = logging.getLogger(__name__)

# -- Static data (install). --
REQUEST_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(REQUEST_DIR) + "/../../"
LOG_DIR = PROJECT_DIR + "data/log/"
execfile(expanduser(PROJECT_DIR+'config_backends.py'))
conf_database = CONF['config_database']

def connect():
    """ Return the database of the project, ready to use."""
    path = PROJECT_DIR + conf_database['path'] + conf_database['file']
    db = dataset.connect('sqlite:///' + path)
    return(db)


def readConfig():
    """ Update (or create) the persistent database accordingly to the config file ./config_backends.py. """
    db = connect()
    ## Users
    table = db['users']
    for user in CONF['users']:
        # We need to extract all information relative to this user that can been stored in some rows.
        # In particular, shortcuts and sendSMS cannot and we deal with them in different tables.
        userDB = {
            'user' : user['login'],
            'name' : user['name'],
            'number' : user['number'],
            'email' : user['email'],
            }
        # Update user (we use the filter 'user' to update only the entry that match user['login'])
        if not(table.update(userDB, ['user'])):
            # or add it if not already present
            table.insert(userDB)
    ## sendSMS
    table = db['sendSMS']
    for user in CONF['users']:
        userSMS = user['sendSMS']
        userDB = {
            'user' : user['login'],
            'method' : userSMS['method']
            }
        if userSMS['method'] == "FREE_API":
            userDB['login'] = userSMS['login']
            userDB['password'] = userSMS['password']
        elif userSMS['method'] == "EMAIL":
            userDB['operateur'] = userSMS['operateur']
        if not(table.update(userDB, ['user'])):
            table.insert(userDB)
    ## Shortcuts
    table = db['shortcuts']
    for user in CONF['users']:
        userShort = user['shortcuts']
        for shortcut in userShort:
            shortKey, shortList = shortcut
            userDB = {
                'user' : user['login'],
                'shortcut' : shortKey,
                'command' : ";".join(shortList)
                }
            if not(table.update(userDB, ['user', 'shortcut'])):
                table.insert(userDB)
    ## Backends
    table = db['backends']
    for backend in CONF['config_backends']:
        backendDB = {
            'backend' : backend,
            'API_key' : CONF['config_backends'][backend]['API_key']
            }
        if not(table.update(backendDB, ['backend'])):
            table.insert(backendDB)
    

def printInfo():
    """ Print all relevant information about the current database. """
    db = connect()
    logging.info("## List of all tables: " + str(db.tables))
    logging.info("## Table Users, size: " + str(len(db['users'])))
    logging.info("# Columns: " + str(db['users'].columns))
    for user in db['users']:
        logging.info(user['user'] + ", name:" + user['name'])
    logging.info("## Table SendSMS, size: " + str(len(db['sendSMS'])))
    logging.info("# Columns: " + str(db['sendSMS'].columns))
    for user in db['sendSMS']:
        logging.info(user['user'] + ", method:" + user['method'])
    logging.info("## Table Users, size: " + str(len(db['shortcuts'])))
    logging.info("# Columns: " + str(db['shortcuts'].columns))
    for short in db['shortcuts']:
        logging.info(short['user'] + ", shortcut: " + short['shortcut'] +
              ", command:" + short['command'])
    logging.info("## Table Backends, size: " + str(len(db['backends'])))
    logging.info("# Columns: " + str(db['backends'].columns))
    for backend in db['backends']:
        logging.info(backend['backend'] + ", API_key: " + backend['API_key'])
    logging.info("## Table Store, size: " + str(len(db['store'])))
    logging.info("# Columns: " + ",".join(db['store'].columns))
    for mess in db['store']:
        logging.info(mess['user'] + ", nb: " + str(mess['nb']) + ", message: " + mess['message'])
    logging.info("## Table yelpIDs, size: " + str(len(db['yelpIDs'])))
    logging.info("# Columns: " + str(db['yelpIDs'].columns))
    for busi in db['yelpIDs']:
        logging.info(busi['user'] + ", nb: " + str(busi['nb']) + ", name: " + busi['name'])
       

def exportJson(tableName='users', filename='toRemove.json'):
    """ Given a tableName (filename is truly optional), it exports
    the whole corresponding table as a json data."""
    db = connect()
    table = db[tableName]
    dataset.freeze(table, format='json', filename=filename)        
    json_data = open(filename)
    data = json.load(json_data)
    json_data.close()
    os.remove(filename)
    return(data)

# LIB:
# https://dataset.readthedocs.org/en/latest/quickstart.html
