# -- coding: utf-8 --
# TODO: 
# - TESTER
# - réfléchir et régle la précision des résultats (adresse seulement pour velib par ex.) et compression des arrêtes métro...
# - introduire d'autres données pour trouver le meilleur journey (pluie sur météoFrance => pas de velib, etc. (trouver d'autres choses)...)
# - ajouter une fonctionnalité 'suivi' : si jamais quelque chose se passe mal, on est prévenu avec une MAJ de l'itinéraire
# 

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
import os 
from os.path import expanduser
import csv
import datetime
import time
import urllib                  # used to transform text into url
import urllib2                  # used to transform text into url
import json
import pprint
from geoOfAddress import listOfChoices

from static import *
from utils import *
from mainClass import *

# -- Setup Logging --
logging = logging.getLogger(__name__)
# -- Static data (install). --
REQUEST_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(REQUEST_DIR) + "/../../"
# -- User Data --
execfile(expanduser(PROJECT_DIR+'config_backends.py'))
pathData = expanduser(PROJECT_DIR+'data/backends/RATP/static/ratp_arret_graphique_01.csv')
navitiaKey = CONF['config_backends']['navitia']['API_key']
prefixQuery ="http://api.navitia.io/v1/coverage/fr-idf/journeys" # limit the coverage to IDF

pp = pprint.pprint

### CONFIG
minDuration = 60                # do not print section with duration <= minDuration
maxCharDirect = 10              # max char. to print for directions

# -----------------
# -- COORDINATES --
# -----------------
def coordsCVS(row):
    return([row[1],row[2]])

def findCoordsStation(name):
    """ Given the name (of part of it), returns GPS coordinates corresponding to the station of same name
    according the the CVS file released by RATP (will fail when misspelled)."""
    # Fetch csv
    with open(pathData, 'rb') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=str('#'), quotechar=str('|'))
        # each row of spamreader is of the form:
        #['11572886', '2.27720907516197', '48.8636777966216', 'POMPE-MAIRIE DU 16E', 'PARIS-16EME', 'bus']
        matched = []
        for row in spamreader:
            if (row[-1] in ["metro", "tram", "rer"]): # (eliminates bus stations)
                toSearch = name.strip().lower()
                if -1 != row[3].strip().lower().decode("utf-8").find(toSearch):
                    matched.append(row)
                    break
        else:
            logging.debug("Did not find any.")
            return []
        if len(matched) > 1:
            for row in matched:
                if (row[-1] in ["metro", "rer"]):
                    return coordsCVS(row)
        return(coordsCVS(matched[0]))

def findPlace(name):
    """ Find a place using MapQuest matching 'name'."""
    listPlaces = listOfChoices(name, 20)
    if listPlaces == None or len(listPlaces) == 0:
        logging.debug("No places found.")
        return None
    # Paris in priority
    for place in listPlaces:
        if "Paris" in place['address']:
            return(place)
    return(listPlaces[0])

def findCoords(name):
    """ Find a place using RATP CVS or MapQuest matching 'name'."""
    coords = findCoordsStation(name)
    if coords == []:
        logging.debug("[findCoords] No station found, we will try with MapQuest.")
        place = findPlace(name)
        if place != None:
            coords = [str(place['geo'][0]), str(place['geo'][1])]
            res = (coords, place['address'].strip())
        else:
            logging.warning("[findCoords] No station found, No place found. Sorry.")
            raise Exception("Nous n'avons pas trouvé d'arrêt correspondat à "+ name)
    else:
        # in that case, we found a RATP station
        res = (coords, ("la station %s" % name).strip())
    logging.debug("Place found %s." % (str(res)))
    return(res)

# ---------------  
# -- JOURNEYS  --
# ---------------
optionsDefault = {
    'bike' : True,              # consider the possibility to rent a Velib
    'speedBike' : 15.,           # speed of biking
    'speedWalk' : 4.3,          # speed of walking
    'lessWalk' : False,         # true: max 10m to reach public transport, 20m otehrwise
    }

def paramOfOptions(opt):
    """ Given options 'opt', build Nativia parameters related to transportation."""
    ratio = 1000./3600.         # km/h -> m/s
    bike = opt['bike']
    max_duration_walk = 10*60 if opt['lessWalk'] else 20*60
    dicoParam = {
        'first_section_mode[]' :  "bss" if bike else "walking" , # bss: bike sharing
        'last_section_mode[]' : "bss" if bike else "walking",
        'max_duration_to_pt' : max_duration_walk,  # max time (in sec.) to reach public transport by bike or walk (default 15m)
        'walking_speed' : '%.3f' % (opt['speedWalk']*ratio), #(4.5km/h) (default: 1.12 m/s (4 km/h))
        'bike_speed' : '%.4f' % (opt['speedBike']*ratio), # (18 km/h) (default: 4.1 m/s (14.7 km/h))
        'bss_speed' : '%.4f' % (opt['speedBike']*ratio), # (18 km/h)  bike haring (default: same)
        }    
    return(dicoParam)

def makeRequest(fromCoords, toCoords, departure=None, arrival=None, optionsJourney = optionsDefault):
    """ Given departure and arrival GPS coordinates, and at most one datetime among (departure, arrival),
    returns the best journey satisfying all constraints (if no datetetime is given, we look for the first one)."""
    # get dateR and dateRepresents (arrival or departure or as soon as possible)
    if departure:
        dateR = departure.strftime("%y%m%dT%H%M")
        dateRepresents = "departure"
    if arrival:
        dateR = arrival.strftime("%y%m%dT%H%M")
        dateRepresents = "arrival"
    if not(departure) and not(arrival):
        dateR = datetime.datetime.now().strftime("%y%m%dT%H%M")
        dateRepresents = "departure"        
    # Todo: cleaner way
    randomStr = "sdf5s6d4f5345sd5f"
    paramDico = {'from' : randomStr.join(fromCoords),
                 'to' : randomStr.join(toCoords),
#                 'commercial_mode' : '',    allows for filtering by transport mode
                 'datetime' : dateR,
                 'datetime_represents' : dateRepresents,
#                 'forbidden_uris[]' : #If you want to avoid lines, modes, networks, etc.
#                 'min_nb_journeys' : Minimum number of different suggested trips More in multiple_journeys
#                 'min_nb_journeys' : Maximum number of different suggested trips More in multiple_journeys
#                 'count' : 100,#Fixed number of different journeys More in multiple_journeys
#                 'max_nb_transfers' : 0,     # default: 10
                 'disruption_active' : True, # take disruptions into account
                 }
    paramDicoOptions = paramOfOptions(optionsJourney)
    paramDico = dict(paramDico, **paramDicoOptions)
    payload = {
        'op': 'login-main',
        'user': navitiaKey,
        'passwd': ''
        }
    params = urllib.urlencode(paramDico)
    # TODO: cleaner way (than replace randomStr)
    URL = (prefixQuery + (str("?%s") % params)).replace(randomStr, ";")
    # create a password manager
    password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
    # Add the username and password.
    # If we knew the realm, we could use it instead of None.
    top_level_url = prefixQuery
    password_mgr.add_password(None, top_level_url, navitiaKey, '') # user=navitiaKey, passwd is empty
    handler = urllib2.HTTPBasicAuthHandler(password_mgr)
    # create "opener" (OpenerDirector instance)
    opener = urllib2.build_opener(handler)
    try:
        # Install the opener.
        # Now all calls to urllib2.urlopen use our opener.
        urllib2.install_opener(opener)
        response = urllib2.urlopen(URL)
    except IOError as e:
        logging.error("BackendRatp > makeRequest > urllib2 | I/O error({0}): {1}".format(e.errno, e.strerror))
        raise Exception(MESS_BUG())
    data = json.load(response, encoding='utf-8')
    return(data)

def parseDate(dateStr):
    """ Parse date as returned by Nativia Api."""
    structDate = time.strptime(dateStr, "%Y%m%dT%H%M%S")
    date = datetime.datetime(*structDate[:6])
    return(date)


###############################
## Pretty printing functions ##
###############################

def printDuration(duration):
    """Print a duration (precision depends on the duration."""
    if duration < 1800:
        return("%sm%ss" % (duration/60, duration % 60))
    elif duration < 2600:
        return("%sm" % (duration/60))
    else:
        return("%sh%sm" % (duration/3600, (duration % 3600)/60))

def printDate(date):
    """Pretty print dates."""
    return(date.strftime("%Hh%Mm%Ss"))

def renameMode(mode):
    """ Pretty print commercial modes."""
    return(mode.lower().replace("rapidtransit", "RER"))

def isStation(palceDico):
    """ Given an object 'place' returned by Nativia, returns true if it is a RATP station."""
    return("stop_point" in place.keys() and "RTP:" in place["stop_point"]["stop_area"]["id"])

def printPlace(place):
    """ Given an object 'place' returned by Nativia, return a pretty string describing the place."""
    # TODO: les infos donnés par Nativia sont trop peu précises quand il s'agit d'une adresse (ex. 38 Avenue Mozart (Paris). On aimerait l'arrondissement !!!
    # on pourrait passer par mapquest ou google API en mode reverse 'coord -> adresses' au moins quand l'arrondissement manque ...
    isStation = ("stop_point" in place.keys() and "RTP:" in place["stop_point"]["stop_area"]["id"])
    name = place["name"]
    if isStation:
        if "(Paris)" in name:
            name = name.split(" (Paris)")[0]
        name = "la station " + name
        return(name.strip())
    if "poi" in place.keys() and "address" in place["poi"]:
        name = name.replace("(Paris)", "").replace("Paris", "")
        name = name + (" (%s)" % (place["poi"]["address"]["label"]))
    # if there is a ZIP code, no city is needed (e.g., (Paris))
    isAr = name.find("750")
    if isAr != -1:
        name = name[0:isAr+5]
    # if "(Paris)" in name:
    #     name = name.replace("(Paris)", "")
    return(name.strip())

def summaryJourneys(journeys):
    """Give a quick overview of all returned journeys (e.g., """
    nb = len(journeys)
    i = 0
    res = ""
    for journey in journeys:
        i += 1
        dateDeparture = parseDate(journey["departure_date_time"])
        dateArrival = parseDate(journey["arrival_date_time"])
        duration = journey["duration"]
        nbTransfers = journey["nb_transfers"]
        typeJ = journey["type"]     # best, rapid, no_train, comfort, fastest, etc.
        logging.debug("Journey: type: %s, duration: %s, nb. transfers: %s." % (typeJ, printDuration(duration), nbTransfers))
        
        # Parsing the response
#        res += ("Départ à %s, arrivé à %s. " % (printDate(dateDeparture), printDate(dateArrival)))
        summaryS = []
        for section in journey["sections"]:
#            pp(section)
            typeS = section["type"]
            durationS = section["duration"]
            # For some types we just stay at the same place
            if typeS == "bss_rent":     # take a velib 
                summaryS.append("velib")
            elif typeS == "waiting" or typeS == "transfer":
                pass
            # Other types (there exist 'from' and 'to')
            else:
                modeS = section["mode"] if "mode" in section.keys() else ""
                fromS, toS = section["from"], section["to"]
                fromNameS, toNameS = printPlace(fromS), printPlace(toS)
                displayInfoS = (section["display_informations"]
                                if "display_informations" in section.keys()
                                else "")
                transferTypeS = (section["transfer_type"]
                                 if "transfer_type" in section.keys()
                                 else "")
                depDateS, arDateS = section["departure_date_time"], section["arrival_date_time"]
                if typeS == "public_transport":
                    typeTransport = renameMode(displayInfoS['commercial_mode'])
                    lineTransport = displayInfoS['code']
                    directionTransport = displayInfoS['direction']
                    if typeTransport == "Tramway":
                        textS = lineTransport
                    else:
                        typeTransport = typeTransport.replace("RapidTransit","RER").replace("Métro","M")
                        textS = ("%s %s" % (typeTransport, lineTransport))
                    summaryS.append(textS)
        res += ("%s : %s (%s) / " % 
                (str(i), (" - ".join(summaryS)), printDuration(duration)))
    return("Liste des itinéraires: "+ res[:-2])

def journey(fromName, toName, departure=None, arrival=None, summary=False):
    """ Given departure and arrival text descriptions, and at most one datetime among (departure, arrival),
    returns the best journey satisfying all constraints (if no datetetime is given, we look for the first one)."""
    logging.info("Starting ratp")
    res = ""
    # Set up the request
    try:
        (fromCoords,fromPrint) = findCoords(fromName)
        (toCoords,toPrint) = findCoords(toName)
    except Exception as inst:
        return(str(inst.args))
    try:
        data = makeRequest(fromCoords, toCoords, departure, arrival)
    except Exception as inst:
        return(str(inst.args))
    # we never use 'links' part of data:
    data = data["journeys"]
    summaryJ = summaryJourneys(data)
    if summary:
        res += summaryJ + "\n"

    logging.debug("Some journeys found:\n %s" % summaryJ)

    # by default we take the first returned journey
    journey = data[0]
#    pprint.pprint(journey)
    dateDeparture = parseDate(journey["departure_date_time"])
    dateArrival = parseDate(journey["arrival_date_time"])
    duration = journey["duration"]
    nbTransfers = journey["nb_transfers"]
    typeJ = journey["type"]     # best, rapid, no_train, comfort, fastest, etc.

    # Parsing the response
    res += ("Trajet de %s à %s (temps: %s). Départ à %s, arrivé à %s." %
           (fromPrint, toPrint, printDuration(duration), printDate(dateDeparture), printDate(dateArrival)))

    for section in journey["sections"]:
        textS = ""
        typeS = section["type"]
        durationS = section["duration"]
        # For some types we just stay at the same place
        if typeS == "waiting":
            if durationS > minDuration:
                textS = "Attendre %s." % printDuration(durationS)
        elif typeS == "transfer":
            if durationS > minDuration:
                textS = "Changement (%s)." % printDuration(durationS)
        # Other types (there exist 'from' and 'to')
        else:
            modeS = section["mode"] if "mode" in section.keys() else ""
            fromS, toS = section["from"], section["to"]
            fromNameS, toNameS = printPlace(fromS), printPlace(toS)
            displayInfoS = (section["display_informations"]
                            if "display_informations" in section.keys()
                            else "")
            transferTypeS = (section["transfer_type"]
                             if "transfer_type" in section.keys()
                             else "")
            depDateS, arDateS = section["departure_date_time"], section["arrival_date_time"]
            if typeS == "bss_rent":     # take a velib 
                textS = ("Prendre un Velib à %s (%s)." % (fromNameS, printDuration(durationS)))
            elif typeS == "bss_put_back": # put back velib
                textS = ("Reposer le Velib à %s (%s)." % (toNameS, printDuration(durationS)))
            elif typeS == "street_network":
                if modeS == "walking":
                    if durationS > minDuration:
                        textS = ("Marcher de %s à %s (%s)." % (fromNameS, toNameS, printDuration(durationS)))
                elif modeS == "bike":         # ride velib 
                    textS = ("Rouler de %s à %s (%s)." % (fromNameS, toNameS, printDuration(durationS)))
                else:
                    print(section)
                    logging.info("="*30 +"\n")
                    pp(section)
                    textS = "QUE DIRE?"
            elif typeS == "public_transport":
                typeTransport = renameMode(displayInfoS['commercial_mode'])
                lineTransport = displayInfoS['code']
                directionTransport = displayInfoS['direction']
                textS = ("Prendre le %s %s jusqu'à %s (%s) (direct.: %s...)." %
                         (typeTransport, lineTransport, toNameS, printDuration(durationS), 
                          directionTransport[0:maxCharDirect]))
            else:
                logging.info("="*30 +"\n")
                pp(section)
                textS = "QUE DIRE?"
        res += textS + "\n"
    return res

def likelyCorrect(a):
    return(True or "Prendre" in a or "Liste" in a)

class BackendRatp(Backend):
    backendName = "ratp"

    def answer(self, request, config):
        """ Parse a request (instance of class Request) and produce the 
        expected answer (in Unicode). """
        fromName = request.argsList[0]
        toName = request.argsList[1]
        # -- Parsing 'liste'
        options = map(lambda s: simplifyText(s), request.argsList[2:])
        summary = "liste" in options
        # -- Parsing time options
        optionsTime = map(lambda s : s.split()[0] if len(s.split()) > 1 else s, request.argsList[2:])
        departure, arrival = datetime.datetime.now(), None
        if ("dep" in optionsTime or "ar" in optionsTime):
            dateArg = request.argsList[2]
            dateRe = simplifyText(dateArg.split()[0])
            hourStr = simplifyText(dateArg.split()[1]) # only hour/minute (e.g., 12h34)
            nowDay = datetime.datetime.now().strftime("%y%m%d")
            structDate = time.strptime(nowDay + "T" + hourStr, "%y%m%dT%Hh%M")
            date = datetime.datetime(*structDate[:5])
            if dateRe == "dep":
                departure,arrival = date, None
            else:
                departure,arrival = None, date
        # -- Parsing transport options
        # optionsDefault = {
        #     'bike' : True,              # consider the possibility to rent a Velib
        #     'speedBike' : 15.,           # speed of biking (default 14.7)
        #     'speedWalk' : 4.3,          # speed of walking (default 4)
        #     'lessWalk' : False,         # true: max 10m to reach public transport, 20m otehrwise
        #     }
        optionsDico = optionsDefault
        if 'pas velib' in options:
            optionsDico['bike'] = False
        if 'pas sport' in options:
            optionsDico['speedBike'] = 14 # to tweak (all speeds)
            optionsDico['speedWalk'] = 4 
        if 'sport' in options:
            optionsDico['speedBike'] = 20
            optionsDico['speedWalk'] = 7
        res = journey(fromName, toName, departure=departure, arrival=arrival,summary=summary)
        return(compactText(res))

    def help(self):
        """ Returns a help message explaining how to use this backend 
        (in Unicode). """
	return("Demandez 'ratp; lieux1; lieux2' pour recevoir le meilleur itinéraire de lieux1 "
               "à lieux2 (adresses, stations, lieux, etc.). Options horaires: 'dep [horaire]' ou"
               "'ar [horaire]' pour préciser l'horaire (format: '12h45') et 'liste' pour avoir"
               "une liste de résumés d'itinéraires possibles. Options moyen de transport: 'pas velib' "
               "quand on ne veut pas de Velib, 'pas sport' pour prendre en compte que l'on veut prendre "
               "son temps en marchant/roulant et dans le cas contraire: 'sport'.")

    def test(self,user):
        """ Test the backend by inputting different requests and check
        the produced answer. Log everything and returns a boolean denoting
        whether the backend is broken or not (False when broken)."""
        reqs = []
        def ap(x):
            reqs.append(Request(user, "ratp", x, [], ""))
        ap(["Balard", "Hoche"])
        ap(["Ranelagh", "les Buttes Chaumont"])
        ap(["Ranelagh", "les Buttes Chaumont", "sport"])
        ap(["Ranelagh", "les Buttes Chaumont", "pas sport"])
        ap(["Ranelagh", "les Buttes Chaumont", "pas velib"])
#        ap(["Balard", "Hoche", "dep bhk"])
        ap(["Tolbiac","Marx-Dormoy", "ar 23h14", "liste"])
        ap(["Bagneux", "Porte de Montreuil", "dep 23h59"])
        ap(["Bagneux", "Porte de Montreuil", "ar 21h22"])
        ap(["Bagneux", "Porte de Montreuil", "ar 21h22", "liste"])
        ap(["Dormoy Paris", "Mosquée de Paris"])
        ap(["Gare Austerliz", "Bastille"])
        ap(["Collège Henry IV", "Rue de Charonne"])
        ap(["Collège Henry IV", "Créteil"])
        ap(["75 rue Riquet","Porte de Vincennes"])
        ap(["50 Rue de la Verrerie, 75004 Paris", "Bagneux"])
        ap(["Porte d'orléans","nation"])
        ap(["Porte d'orléans","nation", "liste"])
        ap(["Bagneux","Chapelle"])
        for r in reqs:
            logging.info("Checking a request [%s]" % r)
            a = self.answer(r, {})
            if a:
                logging.info(a + "\n")
            if not(likelyCorrect(a)):
                return False
        return True

bRatp = BackendRatp()


# TODO:
#==== recherche de lignes:
# https://github.com/CanalTP/navitia/blob/dev/documentation/navitia.io/source/integration.rst#specific-parameters
#ex. https://api.navitia.io/v1/coverage/fr-idf/networks/network:RER/lines

# === recherche de lignes autocomplete
# https://github.com/CanalTP/navitia/blob/dev/documentation/navitia.io/source/integration.rst#public-transport-objects-autocomplete-pt_objects
# ex: https://api.navitia.io/v1/coverage/fr-idf/pt_objects?q=bus%20ratp%209&type[]=line&type[]=route

# ==== recherche de lieux via nativia
# cf. Github /places
# ex: https://api.navitia.io/v1/coverage/fr-idf/places?q=jardin+des+plantes

# ==== 
