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

def velibParisS(where):
    """ Fetch available stations and bikes around a given location."""
    logging.info("Starting velibParis")
    bashPrefix = "boobsize search "
    # bashPrefix2 = "boobsize last_sensor_measure "
    # prefixBikes = "available_bikes"
    # prefixFree = "available_bike_stands"
    # stationChap = ".18040.Paris.jcvelaux"
    # stationDep = "18110.Paris.jcvelaux"
    # stationRiqet = ".18010.Paris.jcvelaux"
    # stationRiquetP = ".18109.Paris.jcvelaux"
    bashC = bashPrefix + where
    logging.info("Before subprocess: %s." % bashC)
    try:
        process = subprocess.Popen(bashC.split(), stdout=subprocess.PIPE)
    except OSError as e:
        logging.error("velibParis > Popen | Execution failed:" + str(e))
        return(MESS_BUG)
    output = process.communicate()[0]
    # PB: only table formatter shows all required info but not adapted for SMS
    # SOL: truncatated 47 first caracters of all lines
    TRUNC = 51
    output_trunc = ""
    listLines = output.splitlines()[2:] # drop the menu
    for line in listLines:
        if len(line) > 1:
            line = line[TRUNC:]
            output_trunc += line + "\n"
    answer = ("J'ai compris que tu voulais avoir les dispos des vélos à "+where+"."
              " Voici ces infos:\n" + output_trunc)
    return(answer)

def likelyCorrect(a):
    return("Available" in a)

class BackendJcdecaux(Backend):
    backendName = BIKES # defined in static.py

    def answer(self, request, config):
        where = request.argsList[0]
        return(velibParisS(where))

    def test(self, user):
        r1 = Request(user, "velo", ["Luxembourg"], [], "")
        r2 = Request(user, "velo", ["Marx Dormoy"], [], "")
        r3 = Request(user, "trafic", ["Denfert Rochereau"], [], "")
        for r in [r1,r2,r3]:
            logging.info("Checking a request [%s]" % r)
            a = self.answer(r, {})
            logging.info(a + "\n")
            if not(likelyCorrect(a)):
                return False
        return True

    
    def help(self):
        return("Tapez 'velo; lieux' pour rechercher les stations Velib les plus proche de 'lieux' et obtenir les disponibilités "
               "en vélos et en bornes libres.")
