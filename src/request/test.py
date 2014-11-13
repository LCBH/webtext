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
from os.path import expanduser
import logging
import handleSMS

# -- Static data (install). --
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

user1 = [ u for u in CONF['users'] if u['login'] == 'luccaH'][0]
user2 = [ u for u in CONF['users'] if u['login'] == 'vincentCA'][0]

def callHandle(content,number):
    return(handleSMS.main(is_testing=True,is_local=True, content=content, number=number))

callHandle("Coucou", user1['number'])
callHandle("Coucou", user2['number'])
callHandle("banque", user1['number'])

# TODO: focus on testing all backends
