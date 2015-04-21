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
import urllib2                  # used to transform text into url
import json
import unicodedata

from mainClass import *
from static import *

# -- Setup Logging --
logging = logging.getLogger(__name__)

API_url = "http://api-ratp.pierre-grimaud.fr/"
API_trafic = API_url + "data/trafic/"
K_trafic = "trafic"
K_pertu_metro = "perburbations"
K_pertu_rer = "perburbations"

METRO = "metro"
RER = "rer"

def trafic_ratp(metro=True, rer=True):
    """Fetch trafic information of RATP network (for metro or/and RER) using API made by
    Paul Grimaud."""
    answ = "Voici l'état du trafic RATP: "
    if rer:
        url = API_trafic + "rer"
        try:
            resp = urllib2.urlopen(url)
        except IOError as e:
            logging.error("trafic_ratp > urllib2 | I/O error({0}): {1}".format(e.errno, e.strerror))
            return(MESS_BUG)
        data = json.load(resp)
        if data[K_trafic] == "normal":
            answ += u"[RER] Aucune perturbation."
        else:
            answ += u"[RER] Perturbations: "
            for ligne,status in data[K_pertu_rer].iteritems():
                if ligne == "":
                        answ = (u"Le bulletin contient une remarque générale. Voici un résumé: ")
                        if len(status) > 80:
                            answ +=  status[0:80] + u"[...]"
                        else:
                            answ += status
                else:
                    answ += u"{" + ligne + u"}" + u": " + status
        answ += u"\n"
    if metro:
        url = API_trafic + "metro"
        try:
            resp = urllib2.urlopen(url)
        except IOError as e:
            logging.error("trafic_ratp > urllib2 | I/O error({0}): {1}".format(e.errno, e.strerror))
            return(MESS_BUG)
        data = json.load(resp)
        if data[K_trafic] == "normal":
            answ += u"[METRO] Aucune perturbation."
        else:
            answ += u"[METRO] Perturbations: "
            for ligne,status in data[K_pertu_metro].iteritems():
                answ += u"{" + ligne + u"}" + u": " + status
    return(answ)

def simplifyText(s):
    """Remove extra blanks, replace uppercase letters by lowercase letters and remove all accents from 's'."""
    s1 = unicode(str(s.strip().lower()), 'utf-8')
    s2 = unicodedata.normalize('NFD', s1).encode('ascii', 'ignore')     
    return(s2)

def likelyCorrect(a):
    return("Aucune" in a or "Voici un" in a or "{" in a)

class BackendTrafic(Backend):
    backendName = TRAFIC # defined in static.py
    
    def answer(self, request, config):
        argsListFormat = map(lambda s: simplifyText(s), request.argsList)
        is_metro = ("metro" in argsListFormat)
        is_rer = ("rer" in  argsListFormat)
        if len(argsListFormat) == 0:
            is_metro = True
            is_rer = True
        return(trafic_ratp(metro=is_metro, rer=is_rer))
    
    def test(self, user):
        r1 = Request(user, "trafic", [], [], "")
        r2 = Request(user, "trafic", ["rer"], [], "")
        r3 = Request(user, "trafic", ["metro"], [], "")
        r4 = Request(user, "trafic", ["metro", "rer"], [], "")
        for r in [r1,r2,r3,r4]:
            logging.info("Checking a request [%s]" % r)
            a = self.answer(r, {})
            logging.info(a + "\n")
            if not(likelyCorrect(a)):
                return False
        return True

    def help(self):
        return("Tapez 'trafic' pour recevoir l'état du trafic RATP (métro et RER)."
               "Vous pouvez limiter la réponse au RER: 'trafic; rer' ou au metro: 'trafic; metro'.")
    

bTrafic = BackendTrafic()
