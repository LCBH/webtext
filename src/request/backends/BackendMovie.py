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
import datetime

from mainClass import *
from static import *

# -- Setup Logging --
logging = logging.getLogger(__name__)

def showtimes_zip(movie, zipcode):
    logging.info("Starting allocine (zip)")
    bashPrefix = "php "+os.path.dirname(os.path.abspath(__file__))+"/allocine/allocine_showtimes_zip.php "
    bashC = bashPrefix+str(movie)+" "+str(zipcode)
    logging.info("Before subprocess: %s." % bashC)
    try:
        process = subprocess.Popen(bashC.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except OSError as e:
        logging.error("showtimes_zip > Popen | Execution failed:" + str(e))
        return(MESS_BUG)
    output = unicode(process.communicate()[0], "utf-8")
    if "error" in output.lower() or len(output) == 0: # TODO: if error occurs in a cinema/movie ?
        logging.info("PHP failed: %s." % output)
        return(MESS_BUG)
    cine = output.split("THEATER")
    day = int(str(datetime.date.today()).split('-')[2])
    answer = ""    
    for c in cine:
        lines = c.split("\n")
        if len(lines) == 1:
            continue
        answer += lines[0]+"\n"
        for i in xrange(1,len(lines)):
            if len(lines[i]) > 4 and int(lines[i].split()[3]) == day :
                answer += lines[i]+"\n"
                if i < len(lines) -1:
                    answer += lines[i+1]+"\n"
                break
    answer = ("J'ai compris que tu voulais avoir "
              "les séances de %s dans le %s, voici "
              "ce que j'ai trouvé:\n" % (str(movie),str(zipcode)) + answer)
    return(answer)



def showtimes_theater(theater):
    logging.info("Starting allocine (theater)")
    bashPrefix = "php "+os.path.dirname(os.path.abspath(__file__))+"/allocine/allocine_showtimes_theater.php "
    bashC = bashPrefix+str(theater)
    logging.info("Before subprocess: %s." % bashC)
    try:
        process = subprocess.Popen(bashC.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except OSError as e:
        logging.error("showtimes_theater > Popen | Execution failed:" + str(e))
        return(MESS_BUG)
    output = unicode(process.communicate()[0], "utf-8")
    if "error" in output.lower() or len(output) == 0: # TODO: if error occurs in a cinema/movie ?
        logging.info("PHP failed: %s." % output)
        return("Erreur avec le backend PHP\nUsage pour cine: 'cine [titre] [zip] ou cine [nom de cinema]'\n")
    movies = output.split("MOVIE")
    day = int(str(datetime.date.today()).split('-')[2])
    answer = ""    
    for c in movies:
        lines = c.split("\n")
        if len(lines) == 1:
            continue
        answer += lines[0]+"\n"
        for i in xrange(1,len(lines)):
            if len(lines[i]) > 4 and int(lines[i].split()[3]) == day :
                answer += lines[i]+"\n"
                # let's get the movies of the day for now, otherwise uncomment the two following lines
                # if i < len(lines) -1:
                #     answer += lines[i+1]+"\n"
                break
    answer = ("J'ai compris que tu voulais avoir "
              "les séances au %s, voici "
              "ce que j'ai trouvé:\n%s" % (str(theater), answer))
    return(answer)

def likelyCorrect(a):
    return("séance" in a.lower() or "séance" in a.lower()) # fix this

class BackendMovie(Backend):
    backendName = MOVIES # defined in static.py

    def answer(self, request, config):
        if len(request.argsList) < 1 or len(request.argsList) > 2:
            return("Mauvais usage. Rappel: " + self.help())
        elif len(request.argsList) == 1:
            return(showtimes_theater(request.argsList[0]))
        else:
            movie = request.argsList[0]
            zipcode = request.argsList[1]
            return(showtimes_zip(movie, zipcode))
        
    def test(self, user):
        r1 = Request(user, "cine", ["louxor"], [], "")
        r2 = Request(user, "cine", ["citizen", "75006"], [], "")
        for r in [r1,r2]:
            logging.info("Checking a request [%s]" % r)
            a = self.answer(r, {})
            logging.info(a + "\n")
            if not(likelyCorrect(a)):
                return False
        return True


    def help(self):
        return("Usage pour cine: 'cine; [titre] ; [zip] pour obtenir les séances du filme [titre] "
               "autour de [zip]. Autre usage: 'cine; [nom de cinema]' pour obtenir toutes les séances "
               "de la journée dans [nom de cinema].")
