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

""" Set up a light database and simple methods to access it. """
from __future__ import unicode_literals # implicitly declaring all strings as unicode strings

import os
import sys
import wget                     # wget command (for api free)
import subprocess               # for launching bash programs
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
    path = PROJECT_DIR + conf_database['path'] + conf_database['file']
    db = dataset.connect('sqlite:///' + path)
    return(db)



# LIB:
# https://dataset.readthedocs.org/en/latest/quickstart.html
