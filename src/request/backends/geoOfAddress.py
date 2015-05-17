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

""" This module provides a mapping from addresses (that may be incomplete or imprecise)
to precise locations with the corresponding latitude/longitude. """

from __future__ import unicode_literals # implicitly declaring all strings as unicode strings

import urllib                  # used to transform text into url
import urllib2                  # used to transform text into url
import logging
import json
import re                       # for regexp and match

# for debugging only
import pprint

# -- Setup Logging --
logging = logging.getLogger(__name__)

# Gives  a geo. localisation of a given address
lat_long_provider = "http://open.mapquestapi.com/nominatim/v1/search.php"
# example:
# url_reverse_geo = "http://open.mapquestapi.com/nominatim/v1/search.php?format=json&q=la+chapelle,+Paris,+France"

# for debugging Only
pp = pprint.PrettyPrinter(indent=4)

def dicoOfChoices(address) :
    """ Given an address, it returns a dictionnary  with all the choices
    (i.e., places matching address) and their attributes."""
    params = urllib.urlencode({'format' : 'json', 'q' : address})
    response = urllib2.urlopen(lat_long_provider + ("?%s" %params))
    data = json.load(response, encoding='utf-8')
    return(data)

def listOfChoices(address, max_nb):
    """ Given an address and an integer X, it returns the list of the full address of
    at most X choices (i.e., places matching address) along with the list of the corresponding
    (latitude,longitude). """
    dico = dicoOfChoices(address)
    lChoices = []
    lChoicesGeo = []
    regexp_arrond = re.compile("^ [0-9]{1,2}e$")
    compt = 0
    while (compt < max_nb and compt < len(dico)):
        choice = dico[compt]
        compt += 1
        osmType = choice['osm_type']
        address = choice['display_name']
        if osmType == 'node' and "France" in address:
            address_words = address.split(',')
            def toRemove(word):
                if word == ' Paris' or '-de-France' in word or " France" in word:
                    return(False)
                if regexp_arrond.match(word):
                    return(False)
                return(True)
            simplified_address = ', '.join(filter(toRemove, address_words))
            lChoices.append(simplified_address)
            lChoicesGeo.append((float(choice['lat']), float(choice['lon'])))
    return(lChoices, lChoicesGeo)

# For debugging only
for e in dicoOfChoices("Dormoy") :
# for e in listOfChoices("Chapelle",4) :
    print "--------------------", e
# (l1,l2) = listOfChoices("Chapelle", 4)
# pp.pprint(l1)
# pp.pprint(l2)


# URL OF THE API'S DOC: 
# http://open.mapquestapi.com/nominatim/
