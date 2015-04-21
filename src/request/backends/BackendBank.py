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

from __future__ import unicode_literals # implicitly declaring all strings as unicode strings

import logging
import subprocess               # for launching bash programs

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
    answer += output
    if details:
        logging.info("More details needed, before subprocess: %s" % bashCommandHistory)
        try:
            process = subprocess.Popen(bashCommandHistory.split(), stdout=subprocess.PIPE)
        except OSError as e:
            logging.error("bankInfo > Popen | Execution failed:" + str(e))
            return(MESS_BUG)
        outputHistory = process.communicate()[0]
        answer += " | Les détails:\n" + outputHistory
    return(answer)
    

def likelyCorrect(a):
    return("Livret" in a)

class BackendBank(Backend):
    backendName = BANK # defined in static.py

    def __init__(self):
        Backend.__init__(self, is_private = True)
        
    def answer(self, request, config):
        if config['is_local']:
            if request.user['login'] == "luccaH":
                if len(request.argsList) > 0 and request.argsList[0].lower().strip() == "details":
                    return(bankInfo(details=True))
                else:
                    return(bankInfo())
            else:
                return(("Pas de backend banque configuré pour l'utilisateur %s." % user['login'])
                       + " Si ça vous intéresse contacter l'administrateur %s pour lui demander de vous configurer un compte." % adminEmail)
        else:
            logging.info("I cannot answer because I am executed on the request server but the data needed are private.")
            return None

    def test(self, user):
        config = {}
        config['is_local'] = True
        r1 = Request(user, "banque", [], [], "")
        r2 = Request(user, "banque", ["details"], [], "")
        for r in [r1,r2]:
            logging.info("Checking a request [%s]" % r)
            a = self.answer(r, config)
            logging.info(a + "\n")
            if not(likelyCorrect(a)):
                return False
        return True

    def help(self):
        return("Attention: ce service n'est disponible que si vous renseignez vos informations de connections. "
               "Contactez l'administrateur (email: %s) pour plus de détails. "
               "Tapez 'banque' pour recevoir le montant actuel sur vos différents comptes. "
               "Tapez 'banque; details' pour recevoir en plus des montants, les dernières transactions." % adminEmail)

bBank = BackendBank()
