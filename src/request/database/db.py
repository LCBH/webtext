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
from datetime import *
import dataset

import utils

# -- Setup Logging --
logging = logging.getLogger(__name__)


def pushMessage(user, messages):
    """ Push a message to the user's queue. """
    hashAnswer = hash(messages[0])
    date = datetime.today()
    dB = utils.connect()
    table = dB['store']
    for nb in range(len(messages)):
        toStore = {
            'user' : user['login'],
            'date' : str(date),
            'message' : messages[nb],
            'hashAnswers' : hashAnswer,
            'nb' : nb,
            }
        table.insert(toStore)

def popMessage(user):
    """ Pop a message to the user's queue. """
    dB = utils.connect()
    table = dB['store']
    elts = table.find_one(user=user['login'])
    # TODO REMOVE ELT
    return(elts[0])

def clearQueue(user):
    """ Clear the user's queue. """
    pass                      # TODO

# TODO:
# - use this databse to store very long answers that would need many SMS to send
# -> requires a kind of state (for each user)
# - use it to sore 'reminders'

# LIB:
# https://dataset.readthedocs.org/en/latest/quickstart.html
