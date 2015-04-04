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
from BackendForecasts import BackendForecasts
from BackendBank import BackendBank
from BackendJcdecaux import BackendJcdecaux
from BackendTrafic import BackendTrafic
from BackendWiki import BackendWiki
# from cine import BackendCine  OUPS

# -- Setup Logging --
logging = logging.getLogger(__name__)

# DOC and EXAMPLES
bForecasts = BackendForecasts()
bBank = BackendBank()
bJcdecaux = BackendJcdecaux()

# print(bForecasts.answer(None, None))
# for b in Backend:
#     print(b)
