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

import logging
from mainClass import *
from static import *

# -- Setup Logging --
logging = logging.getLogger(__name__)

class BackendMovie(Backend):
    backendName = FORECASTS # defined in static.py

    def answer(self, request, config):
        # parse:
            is_metro = ("metro" in request.argsListStrip)
            is_rer = ("rer" in request.argsListStrip)
            if len(request.argsList) == 0:
                is_metro = True
                is_rer = True
            return(fetch.trafic_ratp(optionsDict, metro=is_metro, rer=is_rer))

        return("OK")



