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
    if len(listPlaces) == 0:
        logging.debug("No places found.")
        return None
    # Paris in priority
    for place in listPlaces:
        if "Paris" in place['address']:
            return(place)
    return(listPlaces[0])

def findCoords(name):
    coords = findCoordsStation(name)
    if coords == []:
        logging.info("[findCoords] No station found, we will try with MapQuest.")
        place = findPlace(name)
        if place != None:
            coords = [str(place['geo'][0]), str(place['geo'][1])]
            res = (coords, place['address'])
        else:
            logging.warning("[findCoords] No station found, No place found. Sorry.")
            return "Nous n'avons pas trouvé d'arrêt correspondat à "+toName
    else:
        res = (coords, "Station %s " % name)
    logging.debug("Place found %s." % (str(res)))
    return(res)

# ---------------  
# -- JOURNEYS  --
# ---------------  
def makeRequest(fromCoords, toCoords, departure=None, arrival=None):
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
    ratio = 1000./3600.
    paramDico = {'from' : randomStr.join(fromCoords),
                 'to' : randomStr.join(toCoords),
#                 'commercial_mode' : '',
                 'datetime' : dateR,
                 'datetime_represents' : dateRepresents,
#                 'forbidden_uris[]' : #If you want to avoid lines, modes, networks, etc.
                 # 'first_section_mode[]' : "walking", "bss"
                 # 'last_section_mode[]' : "bss",
                 'max_duration_to_pt' : 20*60, # max time (in sec.) to reach public transport by bike or walk
                 'walking_speed' : 4.5*ratio, #(4.5km/h)         # default: 1.12 m/s (4 km/h)
                 'bike_speed' : 18*ratio, # (18 km/h)           # default: 4.1 m/s (14.7 km/h)
                 'bss_speed' : 18*ratio, # (18 km/h)   bike haring        # default: 4.1 m/s (14.7 km/h)
#                 'min_nb_journeys' : Minimum number of different suggested trips More in multiple_journeys
#                 'min_nb_journeys' : Maximum number of different suggested trips More in multiple_journeys
#                 'count' : Fixed number of different journeys More in multiple_journeys
#                 'max_nb_transfers' : 7,     # default: 10
                 'disruption_active' : True, # take disruptions into account
                 }
    payload = {
        'op': 'login-main',
        'user': navitiaKey,
        'passwd': ''
        }
    params = urllib.urlencode(paramDico)
#    pprint.pprint(params)
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
        logging.error("BackendRatp > urllib2 | I/O error({0}): {1}".format(e.errno, e.strerror))
        raise Exception(MESS_BUG())
    data = json.load(response, encoding='utf-8')
    return(data)

def printDuration(duration):
    if duration < 3600:
        return("%sm%ss" % (duration/60, duration % 60))
    else:
        return("%sh%sm" % (duration/3600, (duration % 3600)/60))

def printDate(date):
    """Pretty print dates."""
    return(date.strftime("%Hh%Mm%Ss"))

def parseDate(dateStr):
    """ Parse date as returned by Nativia Api."""
    structDate = time.strptime(dateStr, "%Y%m%dT%H%M%S")
    date = datetime.datetime(*structDate[:6])
    return(date)

def journey(fromName, toName, departure=None, arrival=None):
    """ Given departure and arrival text descriptions, and at most one datetime among (departure, arrival),
    returns the best journey satisfying all constraints (if no datetetime is given, we look for the first one)."""
    logging.info("Starting ratp")
    # Set up the request
    (fromCoords,fromPrint) = findCoords(fromName)
    (toCoords,toPrint) = findCoords(toName)
    try:
        data = makeRequest(fromCoords, toCoords, departure, arrival)
    except Exception as inst:
        return(str(inst.args))
    # we never use 'links' part of data:
    data = data["journeys"]
    # by default we take the first returned journey
    journey = data[0]
#    pprint.pprint(journey)
    dateDeparture = parseDate(journey["departure_date_time"])
    dateArrival = parseDate(journey["arrival_date_time"])
    duration = journey["duration"]
    nbTransfers = journey["nb_transfers"]
    typeJ = journey["type"]     # best, rapid, no_train, comfort, fastest, etc.

    # Parsing the response
    res = ("Trajet de %s à %s (temps: %s). Départ à %s, arrivé à %s. " %
           (fromPrint, toPrint, printDuration(duration), printDate(dateDeparture), printDate(dateArrival)))
    print(res)

    for section in journey["sections"]:
        typeS = section["type"]
        durationS = section["duration"]
        # For some types we just stay at the same place
        if typeS == "waiting":
            textS = "Attendre %s. " % printDuration(durationS)
        elif typeS == "transfer":
            textS = "Changement (%s). " % printDuration(durationS)
        elif typeS == "bss_rent":     # take a velib 
            print(section)
            logging.info(section)
            textS = ("Prendre un vélo à %s - %s (%s). " % (fromNameS, toNameS, printDuration(durationS)))
        elif typeS == "bss_put_back": # put back velib
            print(section)
            logging.info(section)
            textS = ("Reposer un vélo à %s - %s (%s). " % (fromNameS, toNameS, printDuration(durationS)))
        # Other types (there exist 'from' and 'to')
        else:
            modeS = section["mode"] if "mode" in section.keys() else ""
            fromS, toS = section["from"], section["to"]
            fromNameS, toNameS = fromS["name"], toS["name"]
            displayInfoS = (section["display_informations"]
                            if "display_informations" in section.keys()
                            else "")
            transferTypeS = (section["transfer_type"]
                             if "transfer_type" in section.keys()
                             else "")
            depDateS, arDateS = section["departure_date_time"], section["arrival_date_time"]
            if typeS == "street_network":
                if modeS == "walking":
                    textS = ("Marcher de %s à %s (%s). " % (fromNameS, toNameS, printDuration(durationS)))
                    res += textS
                elif modeS == "bike":         # ride velib 
                    textS = ("Rouler en vélo de %s à %s (%s). " % (fromNameS, toNameS, printDuration(durationS)))
                    res += textS
                else:
                    print(section)
                    logging.info(section)
                    textS = "QUE DIRE?"
            elif typeS == "public_transport":
                typeTransport = displayInfoS['commercial_mode']
                lineTransport = displayInfoS['code']
                directionTransport = displayInfoS['direction']
                textS = ("Prendre le %s %s jusqu'à %s (%s) (direct.: %s...) " %
                         (typeTransport, lineTransport, toNameS, printDuration(durationS), 
                          directionTransport[0:10]))
            else:
                print(section)
                logging.info(section)
                textS = "QUE DIRE?"
        res += textS
        print(textS)            # DEBUG
    return res


# For debugging only
# If this is executed as a script, we parse argv
if __name__ == "__main__":
    # fromName = "Tolbiac"
    # toName = "Marx-Dormoy"
    # print journey(fromName, toName, departure = datetime.datetime.now(), arrival=None)
    fromName = "Tolbiac"
    toName = "Marx-Dormoy"
    print journey(fromName, toName, departure = datetime.datetime.now(), arrival=None)
    fromName = "75 rue Riquet"
    toName = "Porte de Vincennes"
    print journey(fromName, toName, departure = datetime.datetime.now(), arrival=None)
    fromName = "50 Rue de la Verrerie, 75004 Paris"
    toName = "Bagneux"
    print journey(fromName, toName, departure = datetime.datetime.now(), arrival=None)
    # fromName = "Porte d'orléans"
    # toName = "nation"
    # print journey(fromName, toName, departure = datetime.datetime.now(), arrival=None)
    # fromName = "Bagneux"
    # toName = "Chapelle"
    # print journey(fromName, toName, departure = datetime.datetime.now(), arrival=None)

class BackendRatp(Backend):
    backendName = "ratp"

    def answer(self, request, config):
        """ Parse a request (instance of class Request) and produce the 
        expected answer (in Unicode). """
        fromName = request.argsList[0]
        toName = request.argsList[1]
        res = journey(fromName, toName, departure = datetime.datetime.now(), arrival=None)
        return(res)

    def help(self):
        """ Returns a help message explaining how to use this backend 
        (in Unicode). """
	return("Type 'ratp; from;to' to get best journey.")

    def test(self,user):
        """ Test the backend by inputting different requests and check
        the produced answer. Log everything and returns a boolean denoting
        whether the backend is broken or not (False when broken)."""
        fromName = "Bagneux"
        toName = "Porte de Montreuil"
        res = journey(fromName, toName, departure = datetime.datetime.now(), arrival=None)
        if True or not("street" in res):
            return False
        print(res)
        fromName = "Dormoy Paris"
        toName = "Mosquée de Paris"
        res = journey(fromName, toName, departure = datetime.datetime.now(), arrival=None)
        print(res)
        res = journey("Gare Austerliz", "Bastille", departure = datetime.datetime.now(), arrival=None)
        print(res)
        res = journey("Collège Henry IV", "Rue de Charonne", departure = datetime.datetime.now(), arrival=None)
        print(res)
        res = journey("Collège Henry IV", "Créteil", departure = datetime.datetime.now(), arrival=None)
        print(res)
        if not("street" in res):
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
