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

""" Set up a light database and a simple interface. """
from __future__ import unicode_literals # implicitly declaring all strings as unicode strings

import os
import sys
import wget
from os.path import expanduser
import datetime
import json
import logging
import datetime
import dataset

import utils

# -- Setup Logging --
logging = logging.getLogger(__name__)

def dateToInt(date):
    """ We need to convert date into integer because dataset does not handle correctly datetime.datetime objects using SQLite. """
    return(int(10*(date - datetime.datetime(1970,1,1)).total_seconds()))

# ----- MULTIPLE MESSAGES

def pushMessage(user, messages):
    """ Push a message to the user's queue. """
    hashAnswer = hash(messages[0])
    # We store date as Int because dataset does not handle correctly datetime.datetime objects using SQLite
    date = datetime.datetime.now()
    dateInt = dateToInt(date)
    dB = utils.connect()
    table = dB['store']
    for nb in range(len(messages)):
        toStore = {
            'user' : user['login'],
            'dateInt' : dateInt,
            'message' : messages[nb],
            'hashAnswers' : hashAnswer,
            'nb' : nb,
            }
        table.insert(toStore)

def popMessage(user, number=1):
    """ Pop a message to the user's queue. """
    dB = utils.connect()
    table = dB['store']
    # We find the last stored message
    allStore = table.find(user=user['login'], order_by='dateInt')
    allStoreList = list(allStore)
    lastStore = allStoreList[-1]
    # We extract the date and the hash of all stored messages related
    # to the last answer
    dateLast = lastStore['dateInt']
    hashLast = lastStore['hashAnswers']
    lastAnswerMess = table.find(user=user['login'], dateInt=dateLast, hashAnswers=hashLast)
    lastAnswerList = list(lastAnswerMess)
    listMessages = []
    for i in range(min(len(lastAnswerList), number)):
        message = lastAnswerList[0]
        listMessages.append(message['message'])
        table.delete(id = message['id'])
    return(listMessages)

def clearQueue(user):
    """ Clear the user's queue. """
    dB = utils.connect()
    table = dB['store']
    table.delete(user=user['login'])
    
# ----- YELP
labelYelp = "yelpIDs"

def getYelpIDs(user, number=None):
    """ Get list of businesses from previous Yelp request. """
    dB = utils.connect()
    table = dB[labelYelp]
    lastStored = table.find(user=user['login'])
    lastStoredList = list(lastStored)
    listBusinesses = []
    size = (min(len(lastStoredList), number)
            if number 
            else len(lastStoredList))
    for i in range(size):
        business= lastStoredList[i]
        listBusinesses.append(business)
#        table.delete(id = business['id'])
    return(listBusinesses)

def storeYelpIDs(user, listBusinesses):
    """ Store list of businesses of previous request. """
    dB = utils.connect()
    # We first delete previous entries for the user
    table = dB[labelYelp]
    table.delete(user=user['login'])
    # We store the new request
    hashAnswer = hash(str(listBusinesses))
    # We store date as Int because dataset does not handle correctly datetime.datetime objects using SQLite
    date = datetime.datetime.now()
    dateInt = dateToInt(date)
    table = dB[labelYelp]
    for nb in range(len(listBusinesses)):
        toStore = {
            'user' : user['login'],
            'dateInt' : dateInt,
            'hashAnswers' : hashAnswer,
            'yelpID' : listBusinesses[nb]['yelpID'],
            'name' : listBusinesses[nb]['name'],
            'nb' : nb,          # is used to order the list
            }
        table.insert(toStore)

def clearYelpIDs(user):
    """ Clear the user's yelp IDs. """
    dB = utils.connect()
    table = dB[labelYelp]
    table.delete(user=user['login'])

# TODO:
# - use this databse to store very long answers that would need many SMS to send
# -> requires a kind of state (for each user)
# - use it to sore 'reminders'

# LIB:
# https://dataset.readthedocs.org/en/latest/quickstart.html
