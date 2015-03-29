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

def bankInfo(details=False):
    """ Fetch the amounts of bank accounts."""
    logging.info("Starting bankInfo")
    answer = "Banque: "
    bashCommandList = "boobank list --formatter=multiline --select=label,balance"
    bashCommandHistory = ("boobank history 102780735700020237601EUR@creditmutuel "
                          "--formatter=multiline --select=date,raw,amount")
    logging.info("Before subprocess: %s" % bashCommandList)
    try:
        process = subprocess.Popen(bashCommandList.split(), stdout=subprocess.PIPE)
    except OSError as e:
        logging.error("bankInfo > Popen | Execution failed:" + str(e))
        return(MESS_BUG)
    output = process.communicate()[0]
    answer += str(output)
    if details:
        logging.info("More details needed, before subprocess: %s" % bashCommandHistory)
        try:
            process = subprocess.Popen(bashCommandHistory.split(), stdout=subprocess.PIPE)
        except OSError as e:
            logging.error("bankInfo > Popen | Execution failed:" + str(e))
            return(MESS_BUG)
        outputHistory = process.communicate()[0]
        answer += " | Les détails:\n" + str(outputHistory)
    return(answer)
    

class BackendBank(Backend):
    backendName = BANK # defined in static.py

    def __init__(self):
        Backend.__init__(self, is_private = True)
        
    def answer(self, request, config):
        if config['is_local']:
            if user['login'] == "luccaH":
                if len(request.argsList) > 0 and request.argsList.lower() == "details":
                    return(fetch.bankInfo(details=True))
                else:
                    return(fetch.bankInfo())
            else:
                return(("Pas de backend banque configuré pour l'utilisateur %s." % user['login'])
                       + " Si ça vous intéresse contacter l'administrateur %s pour lui demander de vous configurer un compte." % adminEmail)
        else:
            logging.info("I cannot answer because I am executed on the request server but the data needed are private.")
            return None
