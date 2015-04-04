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
import subprocess
import os 
from os.path import expanduser
import csv
import datetime
import urllib                  # used to transform text into url
import urllib2                  # used to transform text into url
import json
import pprint

# from static import *
# from mainClass import *

# -- Setup Logging --
logging = logging.getLogger(__name__)

# -- Static data (install). --
REQUEST_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(REQUEST_DIR) + "/../../"
# -- User Data --
execfile(expanduser(PROJECT_DIR+'config_backends.py'))
pathData = expanduser(PROJECT_DIR+'data/backends/RATP/static/ratp_arret_graphique_01.csv')
navitiaKey = CONF['config_backends']['navitia']['API_key']
prefixQuery ="http://api.navitia.io/v1/journeys"

def coords(row):
    return(row[1:3])

def findCoordsStation(name):
    """ Given the name (of part of it), returns GPS coordinates corresponding to the station of same name.."""
    # Fetch csv
    with open(pathData, 'rb') as csvfile:
        spamreader = csv.reader(csvfile, delimiter='#', quotechar='|')
        # each row of spamreader is of the form:
        #['11572886', '2.27720907516197', '48.8636777966216', 'POMPE-MAIRIE DU 16E', 'PARIS-16EME', 'bus']
        matched = []
        for row in spamreader:
            if (row[-1] in ["metro", "tram", "rer"]): # (eliminates bus stations)
                if -1 != row[3].strip().lower().find(name.strip().lower()):
                    matched.append(row)
                    break
        if len(matched) > 1:
            for row in matched:
                if (row[-1] in ["metro", "rer"]):
                    return coords(row)
        return(coords(matched[0]))
        
#TODO: ajouter la possibilité de tester en local (sans internet) avec un json en dump file
def makeRequest(fromCoords, toCoords, departure=None, arrival=None, isTesting=False):
    """ Given departure and arrival GPS coordinates, and at most one datetime among (departure, arrival),
    returns the best journey satisfying all constraints (if no datetetime is given, we look for the first one)."""
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
                 'commercial_mode' : 'metro',
                 'datetime' : dateR,
                 'datetime_represents' : dateRepresents
                 }
    payload = {
        'op': 'login-main',
        'user': navitiaKey,
        'passwd': ''
        }
    params = urllib.urlencode(paramDico)
    URL = (prefixQuery + (str("?%s") %params)).replace(randomStr, ";")
    # create a password manager
    password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
    # Add the username and password.
    # If we knew the realm, we could use it instead of None.
    top_level_url = prefixQuery
    password_mgr.add_password(None, top_level_url, navitiaKey, '') # user=navitiaKey, passwd is empty
    handler = urllib2.HTTPBasicAuthHandler(password_mgr)
    # create "opener" (OpenerDirector instance)
    opener = urllib2.build_opener(handler)
    # use the opener to fetch a URL
    opener.open(URL)
    # Install the opener.
    # Now all calls to urllib2.urlopen use our opener.
    urllib2.install_opener(opener)
    response = urllib2.urlopen(URL)
    data = json.load(response, encoding='utf-8')
    return(data)

      
def journey(fromName, toName, departure=None, arrival=None):
    """ Todo."""
    logging.info("Starting ratp")
    # Todo

# for debugging Only
pp = pprint.PrettyPrinter(indent=4)
coords1 = findCoordsStation("Chapelle")
coords2 = findCoordsStation("bagneux")
print(";".join(coords1))
print(coords2)
pp.pprint(makeRequest(coords1, coords2, departure = datetime.datetime.now()))

# Uncomment and fill in to add the backend:
# def likelyCorrect(answer):
#     return("Vent" in answer)

# class BackendForecasts(Backend):
#     backendName = FORECASTS # defined in static.py

#     def answer(self, request, config):
#         where = request.argsList[0]
#         return(forecasts(where, config))

#     def test(self, user):
#         return("TODO")

#     def help(self):
#         return("TODO")
  
