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

class BackendWiki(Backend):
    backendName = WIKI # defined in static.py

    def answer(self, request, config):
        # Parse:
            # if len(request.argsList) > 1:
            #     if (len(request.argsList) <> 2 or
            #         ("fr" <> request.argsList[1].lower.strip()) and "en" <> request.argsList[1].lower().strip()):
            #         return ("Usage pour wiki: la requête en premier argument et la langue (fr ou en) en second argument"
            #                 "(optionnel).")
            #     else:
            #         lang = request.argsList[1].lower().strip()
            #         return(fetch.wikiSummary(optionsDict, query=request.argsList[0], language=lang))
            # else:
            #     return(fetch.wikiSummary(optionsDict, query=request.argsList[0]))

        return("OK")



