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

""" Fetch different types of information using Weboob and some APIs and pretty
format as a SMS' text."""

from __future__ import unicode_literals # implicitly declaring all strings as unicode strings

import os
import sys
import wget                     # wget command (for api free)
import subprocess               # for launching bash programs
import urllib                   # used to transform text into url
import urllib2                  # used to transform text into url
import logging
from os.path import expanduser
import datetime
import json

# -- Setup Logging --
logging = logging.getLogger(__name__)


# API WIKIPEDIA:
# https://wikipedia.readthedocs.org/en/latest/quickstart.html#quickstart

# API paul grimaud (horaires-ratp-api et trafic):
# https://github.com/pgrimaud/horaires-ratp-api
