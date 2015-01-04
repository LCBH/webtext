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
import wikipedia

import backends.jcdecaux

# -- Setup Logging --
logging = logging.getLogger(__name__)

def forecasts(options, zipcode):
    """ Fetch forecasts in Zipcode."""
    logging.info("Starting bankInfo")
    bashCommandList = ("wetboobs forecasts %s" % zipcode)
    logging.info("Before subprocess: %s" % bashCommandList)
    process = subprocess.Popen(bashCommandList.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]
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

def wikiSummary(options, query,language="fr"):
    """Fetch the summary of Wikipadia's articles. """
    # language: "en" pour l'anglais et "fr" pour le français
    wikipedia.set_lang(language)
    nb_results = 3
    results = wikipedia.search(query, results=3)
    answ = u"[WIKIPEDIA] "
    if len(results) == 0:
        answ += u"Aucun article ne correspond à votre requête. Essayez avec une requête plus petite."
        return(answ)
    if len(results) > 1:
        answ += (u"Plusieurs articles répondent à votre requête. J'ai choisi le premier. Voici la liste: "
                 + str(results) + u"\n")
    title = results[0]
    logging.info(title)
    summary = wikipedia.summary(title)
    logging.info(summary)
    answ += (u"Voici le résumé: " + summary)
    return(answ[0:800]) # TODO: better handling of very long mess

def bankInfo(options, details=False):
    """ Fetch the amounts of bank accounts."""
    logging.info("Starting bankInfo")
    bashCommandList = "boobank list --formatter=multiline --select=label,balance"
    bashCommandHistory = ("boobank history 102780735700020237601EUR@creditmutuel "
                          "--formatter=multiline --select=date,raw,amount")
    logging.info("Before subprocess: %s" % bashCommandList)
    process = subprocess.Popen(bashCommandList.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]
    if details:
        logging.info("More details needed, before subprocess: %s" % bashCommandHistory)
        process = subprocess.Popen(bashCommandHistory.split(), stdout=subprocess.PIPE)
        outputHistory = process.communicate()[0]
        output = output + "||| Les détails:\n" + str(outputHistory)
    answer = ("J'ai compris que tu voulais un point sur tes comptes:\n" +
              str(output))
    return(answer)

def velibParis(options, where, config_backends):
    """ Fetch available stations and bikes around a given location."""
    logging.info("Starting velibParis")
    # for now, we delegate the job to the dedicated backend.
    # -> todo: better architecure
    return(backends.jcdecaux.searchVelib(where))

def velibParisS(options, where, config_backends):
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
    process = subprocess.Popen(bashC.split(), stdout=subprocess.PIPE)
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

def trafic_ratp(options, metro=True, rer=True):
    """Fetch trafic information of RATP network (for metro or/and RER) using API made by
    Paul Grimaud."""
    API_url = "http://api-ratp.pierre-grimaud.fr/"
    API_trafic = API_url + "data/trafic/"
    K_trafic = "trafic"
    K_pertu_metro = "perburbations"
    K_pertu_rer = "perburbations"
    answ = u"J'ai compris que tu voulais connaitre l'état du trafic RATP. "
    if rer:
        url = API_trafic + "rer"
        data = json.load(urllib2.urlopen(url))
        if data[K_trafic] == "normal":
            answ += u"[RER] Aucune perturbation.\n"
        else:
            answ += u"[RER] Perturbations: "
            for ligne,status in data[K_pertu_rer].iteritems():
                if ligne == "":
                    answ = (u"Le bulletin contient une remarque générale. Voici une résumé: "
                            + status[0:80] + u"[...]")
                else:
                    answ += u"{" + ligne + u"}" + u": " + status
        answ += u"\n"
    if metro:
        url = API_trafic + "metro"
        data = json.load(urllib2.urlopen(url))
        if data[K_trafic] == "normal":
            answ += u"[METRO] Aucune perturbation.\n"
        else:
            answ += u"[METRO] Perturbations: "
            for ligne,status in data[K_pertu_metro].iteritems():
                answ += u"{" + ligne + u"}" + u": " + status
        answ += u"\n"
    return(answ)

def showtimes_zip(movie, zipcode):
    logging.info("Starting allocine (zip)")
    bashPrefix = "php "+os.path.dirname(os.path.abspath(__file__))+"/backends/allocine_showtimes_zip.php "
    bashC = bashPrefix+str(movie)+" "+str(zipcode)
    logging.info("Before subprocess: %s." % bashC)
    process = subprocess.Popen(bashC.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = unicode(process.communicate()[0], "utf-8")
    if "error" in output.lower() or len(output) == 0: # TODO: if error occurs in a cinema/movie ?
        logging.info("PHP failed: %s." % output)
        return("Erreur avec le backend PHP\nUsage pour cine: 'cine [titre] [zip] ou cine [nom de cinema]'\n")
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
    process = subprocess.Popen(bashC.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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
