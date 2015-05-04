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

""" Gather all implemented backends and crate corresponding instances. """

import logging

from static import *

from mainClass import *
# For each backend, import the corresponding instance here:
from BackendForecasts import bForecasts
from BackendBank import bBank
from BackendJcdecaux import bJcdecaux
from BackendTrafic import bTrafic
from BackendWiki import bWiki
from BackendMovie import bMovie
from BackendYelp import bYelp
from BackendAdmin import bAdmin
#from BackendRatp import bRatp
from BackendAdd import bAdd

# -- Setup Logging --
logging = logging.getLogger(__name__)

backendsList = []
for backend in Backend:
    backendsList.append(backend)

logging.info("Loaded %d backends: %s." %
             (len(backendsList), 
              map(lambda b:b.backendName, backendsList)))
