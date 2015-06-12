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
import urllib                  # used to transform text into url
import urllib2                  # used to transform text into url
import json
import pprint

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
prefixQuery ="http://api.navitia.io/v1/journeys"

def coords(row):
    return(row[1:3])

def findCoordsStation(name):
    """ Given the name (of part of it), returns GPS coordinates corresponding to the station of same name.."""
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
            print "Did not find any."
            return []
        if len(matched) > 1:
            for row in matched:
                if (row[-1] in ["metro", "rer"]):
                    return coords(row)
        return(coords(matched[0]))
        
#TODO: ajouter la possibilité de tester en local (sans internet) avec un json en dump file
def makeRequest(fromCoords, toCoords, departure=None, arrival=None, isTesting=None):
    """ Given departure and arrival GPS coordinates, and at most one datetime among (departure, arrival),
    returns the best journey satisfying all constraints (if no datetetime is given, we look for the first one)."""
    if isTesting != None:
        f = open(isTesting, "r")
        raw = f.read()
        data = json.dump(raw, encoding='utf-8')
        # data = json.load(raw, encoding='utf-8')
        return data
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
#                 'commercial_mode' : '',
                 'datetime' : dateR,
                 'datetime_represents' : dateRepresents,
#                 'max_duration_to_pt' : 30*60, # max time (in sec.) to reach public transport by bike or walk
                 'walking_speed' : 1.26, #(4.5km/h)         # default: 1.12 m/s (4 km/h)
                 'bike_speed' : 5.02, # (18 km/h)           # default: 4.1 m/s (14.7 km/h)
                 'bss_speed' : 5.02, # (18 km/h)   bike haring        # default: 4.1 m/s (14.7 km/h)
                 'disruption_active' : True, # take disruptions into account
#                 'max_nb_transfers' : 0,     # test for velib
                 # 'first_section_mode[]' : "walking",
                 # 'first_section_mode[]' : "bss",
                 # 'last_section_mode[]' : "walking",
                 # 'last_section_mode[]' : "bss",
                 }
    payload = {
        'op': 'login-main',
        'user': navitiaKey,
        'passwd': ''
        }
    params = urllib.urlencode(paramDico)
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
    # use the opener to fetch a URL
    opener.open(URL)
    # Install the opener.
    # Now all calls to urllib2.urlopen use our opener.
    urllib2.install_opener(opener)
    response = urllib2.urlopen(URL)
    data = json.load(response, encoding='utf-8')
    return(data)

def journey(fromName, toName, departure=None, arrival=None, isTesting=None):
    """ Todo."""
    logging.info("Starting ratp")
    fromCoords = findCoordsStation(fromName)
    toCoords = findCoordsStation(toName)
    if toCoords == []:
        return "Nous n'avons pas trouvé d'arrêt correspondat à "+toName
    if fromCoords == []:
        return "Nous n'avons pas trouvé d'arrêt correspondat à "+fromName
    data = makeRequest(fromCoords, toCoords, departure, arrival, isTesting=isTesting)
    arrivalTime = decode_time(data["journeys"][0]["arrival_date_time"].encode("utf8"))

#    pprint.pprint(data)
    res = ""
    for edge in data["journeys"][0]["sections"]:
        res += "[" + edge["type"] + "] " + str(float(edge["duration"])/60.0) + "m\n"
        if edge["type"]== "bss_rent" or edge["type"] == "bss_put_back":
            res += ("  " + edge["from"]["name"] + "--> " + edge["to"]["name"] + "\n")
        if edge["type"]== "street_network":
            res += ("  " + edge["from"]["name"] + "--> " + edge["to"]["name"]+"\n")
            res += ("   --> " + edge["mode"] + "\n")
        if edge["type"] == "public_transport":
            res += ("   " + edge["from"]["name"] + "--> " + edge["to"]["name"] + "\n")
            res += ("    --> métro " + edge["display_informations"]["code"].encode("utf8")+"\n")

            # break
    departureTime = decode_time(edge['departure_date_time'].encode("utf8"))
    firstStop = edge["from"]["name"].encode("utf8")
    network = "RER"
    # if edge["display_informations"]["network"] == "RATP":
    #     network = "métro"

    # line = network + " "+edge["display_informations"]["code"].encode("utf8")


    
    # ret = "J'ai compris que tu souhaitais un itinéraire de %s à %s\nIl faut prendre la ligne %s à %s à %s. Arrivée prévu à %s." %(fromName,
    #                                                                                                                                toName,
    #                                                                                                                                line,
    #                                                                                                                                firstStop,
    #                                                                                                                                departureTime,
    #                                                                                                                                arrivalTime)
#    return ret
    return res

def decode_time(time):
    yearmonthday = time.split("T")[0]
    hoursminsec  = time.split("T")[1]
    year = yearmonthday[0:4]
    month = yearmonthday[4:6]
    day = yearmonthday[6:8]
    hours = hoursminsec[0:2]
    minutes = hoursminsec[2:4]
    secs  = hoursminsec[4:6]
    return (":".join([hours, minutes, secs]))+ " le " + ("/".join([day, month, year]))

# for debugging Only
# pp = pprint.PrettyPrinter(indent=4)
# coords1 = findCoordsStation(fromName)
# coords2 = findCoordsStation(toName)
# print(";".join(coords1))
# print(coords2)
# data = makeRequest(coords1, coords2, departure = datetime.datetime.now(), arrival=None, isTesting = None)
# pp.pprint(data.keys())
# print "-----------------------------------------------"
# # pp.pprint(data["journeys"][0])
# # pp.pprint(len(data["journeys"]))
# arrivalTime = decode_time(data["journeys"][0]["arrival_date_time"].encode("utf8"))
# print "-----------------------------------------------"
# for edge in data["journeys"][0]["sections"]:
#     if edge["type"] == "public_transport":
#         pp.pprint(edge)
#         break
# departureTime = decode_time(edge['departure_date_time'].encode("utf8"))
# firstStop = edge["from"]["name"].encode("utf8")
# network = "RER"
# if edge["display_informations"]["network"] == "RATP":
#     network = "métro"

# line = network + " "+edge["display_informations"]["code"].encode("utf8")


# #departureTime.encode('utf-8') 
# #firstStop.encode('utf-8')
# # line.encode('utf-8')


fromName = "Tolbiac"
toName = "Marx-Dormoy"
print journey(fromName, toName, departure = datetime.datetime.now(), arrival=None, isTesting = None)

fromName = "Porte d'orléans"
toName = "nation"
print journey(fromName, toName, departure = datetime.datetime.now(), arrival=None, isTesting = None)

fromName = "Bagneux"
toName = "Chapelle"
print journey(fromName, toName, departure = datetime.datetime.now(), arrival=None, isTesting = None)

class BackendRatp(Backend):
    backendName = "ratp"

    def answer(self, request, config):
        """ Parse a request (instance of class Request) and produce the 
        expected answer (in Unicode). """
        fromName = request.argsList[0]
        toName = request.argsList[1]
        res = journey(fromName, toName, departure = datetime.datetime.now(), arrival=None, isTesting = None)
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
        res = journey(fromName, toName, departure = datetime.datetime.now(), arrival=None, isTesting = None)
        return("street" in res)


bRatp = BackendRatp()
