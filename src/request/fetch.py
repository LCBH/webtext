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

""" Fetch different types of information using Weboob and some APIs and pretty
format as a SMS' text."""

from __future__ import unicode_literals # implicitly declaring all strings as unicode strings

import os
import sys
import wget                     # wget command (for api free)
import subprocess               # for launching bash programs
import urllib                   # used to transform text into url
import urllib2                  # used to transform text into url
import logging
from os.path import expanduser
import datetime
import json

import backends.jcdecaux
from backends import *

# -- Setup Logging --
logging = logging.getLogger(__name__)



def bankInfo(options, details=False):
    """ Fetch the amounts of bank accounts."""
    logging.info("Starting bankInfo")
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
    if details:
        logging.info("More details needed, before subprocess: %s" % bashCommandHistory)
        try:
            process = subprocess.Popen(bashCommandHistory.split(), stdout=subprocess.PIPE)
        except OSError as e:
            logging.error("bankInfo > Popen | Execution failed:" + str(e))
            return(MESS_BUG)
        outputHistory = process.communicate()[0]
        output = output + "||| Les détails:\n" + str(outputHistory)
    answer = ("J'ai compris que tu voulais un point sur tes comptes:\n" +
              str(output))
    return(answer)

def showtimes_zip(movie, zipcode):
    logging.info("Starting allocine (zip)")
    bashPrefix = "php "+os.path.dirname(os.path.abspath(__file__))+"/backends/allocine_showtimes_zip.php "
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
    bashPrefix = "php "+os.path.dirname(os.path.abspath(__file__))+"/backends/allocine_showtimes_theater.php "
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


# API WIKIPEDIA:
# https://wikipedia.readthedocs.org/en/latest/quickstart.html#quickstart

# API paul grimaud (horaires-ratp-api et trafic):
# https://github.com/pgrimaud/horaires-ratp-api
