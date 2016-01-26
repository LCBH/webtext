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
import subprocess

from static import *
from mainClass import *
from utils import compactText
import tempfile
import time


# -- Setup Logging --
logging = logging.getLogger(__name__)

def forecasts(zipcode, config):
    """ Fetch forecasts in Zipcode."""
    logging.info("Starting forecasts")
   # (dirty) launch_wetboobs.sh is because wetboob is broken
#    bashCommandList = "sh " + (os.path.dirname(os.path.abspath(__file__))+ "/launch_wetboobs.sh %s" % (zipcode))
    bashCommandList = "wetboobs forecasts " + zipcode 
    logging.info("Before subprocess: %s" % bashCommandList)
    try:
        f = tempfile.TemporaryFile() 
        p = subprocess.Popen(bashCommandList.split(), stdout=f) # stdout=subprocess.PIPE)
        time.sleep(2)
        
        # kill process
    #NOTE: if it doesn't kill the process then `p.wait()` blocks forever
        p.terminate() 
        p.wait() # wait for the process to terminate otherwise the output is garbled

    # print saved output
        f.seek(0) # rewind to the beginning of the file
        output = f.read() 
        f.close()

    except OSError as e:
        logging.error("forecasts > Popen | Execution failed:" + str(e))
        return(MESS_BUG())

    # print("OK")
    # time.sleep(2)
    # process.terminate() 
    # process.wait() # wait for the process to terminate otherwise the output is garbled    

    process = 0
    # output = process.communicate()[0]
    output_trunc = u""
    listLines = output.splitlines()
    for line in listLines:
        if len(line) > 1:
            output_trunc += line.decode('utf-8') + u" "
            if line.decode("ascii", "ignore").find("UV") >= 1 or line.decode("ascii", "ignore").find("Indice") >= 1:
                output_trunc += u"\n"
    answer = ((u"J'ai compris que tu voulais la météo dans %s:\n" % zipcode) +
              output_trunc[0:800]) # TODO: better handling of very long mess
    return(answer)

def likelyCorrect(answer):
    return("Vent" in answer)

class BackendForecasts(Backend):
    backendName = FORECASTS # defined in static.py

    def answer(self, request, config):
        where = request.argsList[0]
        return(compactText(forecasts(where, config)))

    def test(self, user):
        r1 = Request(user, "meteo", ["75020"], [], "")
        r2 = Request(user, "meteo", ["Suzette"], [], "")
        logging.info("Checking a request [%s]" % r1)
        a1 = self.answer(r1, {})
        if not(likelyCorrect(a1)):
            return False
        else:
            logging.info("Checking a request [%s]" % r2)
            a2 = self.answer(r2, {})
            return(likelyCorrect(a2))
        
    def help(self):
        return(
            "Il suffit de donner une code postal (français) en argument. "
            "Par exemple: 'meteo; 75020' ou 'meteo; 84000'. "
            "Vous recevrez alors les prévisions pour les prochains jours par texto. "
            "Si tout ne tient pas en un texto, n'oubliez pas qu'il suffit d'envoyer "
            " 'plus' ou 'tout' pour le reste de la réponse."
            )

bForecasts = BackendForecasts()
