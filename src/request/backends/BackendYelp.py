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

from yelpapi import YelpAPI

import logging
import subprocess
import os 
from os.path import expanduser
import csv
import datetime
import json
import pprint

from static import *
from utils import *
from mainClass import *
import database.db

# -- Setup Logging --
logging = logging.getLogger(__name__)
# -- Static data (install). --
REQUEST_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(REQUEST_DIR) + "/../../"
# -- User Data --
execfile(expanduser(PROJECT_DIR+'config_backends.py'))
yelpConf = CONF['config_backends']['yelp']
consumer_key = yelpConf['consumer_key']
consumer_secret = yelpConf['consumer_secret']
token = yelpConf['token']
token_secret = yelpConf['token_secret']

# Yelp requests including credentials
yelp_api = YelpAPI(consumer_key, consumer_secret, token, token_secret)

        # yelp_api.search_query(term='ice cream', location='Paris, France', sort=2, limit=5)
        # yelp_api.search_query(term='ice cream', location='austin, tx', sort=2, limit=5)
        # yelp_api.search_query(category_filter='bikerentals', bounds='37.678799,-123.125740|37.832371,-122.356979', limit=5)
        # yelp_api.business_query(id='amys-ice-creams-austin-3')

DETAILS = "details"
NO_LIMIT_CHAR = "tout"
NB_BUSI = 10                    # number of businesses displayed for each search
MAX_CHAR_REVIEW = 200           # maximum characater displayed for each review
SORT_MODE = 0                   # 0: best matches, 1:distance, 2:ratings (see [1])

# TEXTS
NOT_FOUND = "Yelp n'a pas trouvé de réponses à votre requête."
CRIT_ERROR = "Erreur YELP grave: "
DETAIL = "Détails du lieux "
BAD_REQ = "Requête mal formée. Rappel: "
BAD_INDEX = "Votre dernière requête comportait moins de %d réponses. Rappel: "
LIST = "Liste: "
RATE = 'Note: '

def printLocation(location):
    """ Pretty print location given by Yelp. """
    if "France" in location[-1]:
        location = location[0:-1]
    if "Paris" in location[-1]:
        location[-1] = location[-1].split()[0]
    if len(location) > 2 and "ème" in location[-2]:
        location = location[0:-1]
    return(", ".join(location))

def listBusinesses(request, typeB, location):
    """ Produce the list of businesses of 'typeB' in 'location' (request of type 1). """
    try:                        # Yelp Error
        try:                    # IO error
            dicoBusinesses =  yelp_api.search_query(cc="FR", lang="fr", term=typeB, location=location, sort=SORT_MODE, limit=NB_BUSI)
        except IOError as e:
            logging.error("BackendYelp > Access to the Yelp's API | I/O error({0}): {1}".format(e.errno, e.strerror))
            return(MESS_BUG())
    except YelpAPI.YelpAPIError as e:
        loging.critical(CRIT_ERROR + e)
        return(produceMessBug())
    listBusinesses = dicoBusinesses['businesses']
    database.db.storeYelpIDs(request.user, listBusinesses)
    if len(listBusinesses) == 0:
        return(NOT_FOUND)
    answ = ""
    i = 1
    for busi in listBusinesses:
        # TODO: check que is_closed est toujours faux (filtre?)
        answ += ("(%d) %s : [%d/5] (%d %s), %s.\n"
                 % (i,
                    busi['name'],
                    busi['rating'],
                    busi['review_count'],
                    "reviews" if busi['review_count'] > 1 else "review",
                    printLocation(busi['location']['display_address'])))
        i += 1
    return(answ)

def detailsBusiness(request, idBusiness, no_limit_char_review=False):
    """ Give detailed information (reviews, phone nb., etc.) about one answer of a specific business (request of type 2). """
    try:                        # Yelp error
        try:                    # IO error
            reqBusiness = yelp_api.business_query(cc="FR", lang="fr", id=idBusiness)
        except IOError as e:
            logging.error("BackendYelp > Access to the Yelp's API | I/O error({0}): {1}".format(e.errno, e.strerror))
            return(MESS_BUG())
    except YelpAPI.YelpAPIError as e:
        loging.critical(CRIT_ERROR + e)
        return(produceMessBug())
    answ = (DETAIL + "%s: [%d/5] (%d %s) (%s, %s).\n"
            % (reqBusiness['name'],
               reqBusiness['rating'],
               reqBusiness['review_count'],
               "reviews" if reqBusiness['review_count'] > 1 else "review",
               reqBusiness['display_phone'] if 'display_phone' in reqBusiness else "(pas de tel.)",
               printLocation(reqBusiness['location']['display_address'])))
    # Problem: Yelp's API only provide reviews snippet
    for review in reqBusiness['reviews']:
        if no_limit_char_review:
            textReview = review['excerpt']
        else:
            if MAX_CHAR_REVIEW > len(review['excerpt']):
                maxi = MAX_CHAR_REVIEW
                suff = "[...]"
            else:
                maxi = len(review['excerpt'])
                suff = ""
            textReview = review['excerpt'][0:maxi] + suff
        answ += (RATE + '%d -- %s\n' % (review['rating'], textReview))
    return(answ)


def likelyCorrect(answer):
    return(answer and ("(1)" in answer or RATE in answer))

class BackendYelp(Backend):
    backendName = YELP
    
    def answer(self, request, config):
        # Identify type of Yelp requests
        args = request.argsList
        fstWord = args[0].split()[0]
        if simplifyText(str(fstWord)) == str(DETAILS):
            # request of type 2
            if len(args[0].split()) != 2:
                print(BAD_REQ + self.help())
            else:
                number = int(args[0].split()[1])-1
                dicoBusinesses = database.db.getYelpIDs(request.user, number=NB_BUSI)
                if not(number in range(len(dicoBusinesses))):
                    print(BAD_INDEX % (number + 1) + self.help())
                else:
                    business = dicoBusinesses[number]
                    idBusiness = business["id"]
                    if NO_LIMIT_CHAR in map(lambda s:simplifyText(str(s)), args):
                        return(detailsBusiness(request, idBusiness, no_limit_char_review=True))
                    else:
                        return(detailsBusiness(request, idBusiness))
        else:
            # request of type 1
            if len(args) != 2:
                print(BAD_REQ + self.help())
            else:
                return(LIST + listBusinesses(request, args[0],args[1]))

    def test(self, user):
        reqs = []
        reqs.append(Request(user, "yelp", ["glacier", "75, rue Riquet, Paris"], [], ""))
        reqs.append(Request(user, "yelp", ["indien", "Métro Nation, Paris"], [], ""))
        reqs.append(Request(user, "yelp", [DETAILS + " 2"], [], ""))
        reqs.append(Request(user, "yelp", [DETAILS + " 1"], [], ""))
        reqs.append(Request(user, "yelp", [DETAILS + " 1", NO_LIMIT_CHAR], [], ""))
        reqs.append(Request(user, "yelp", ["pizzeria", "Rue des Teinturiers, Avignon"], [], ""))
        reqs.append(Request(user, "yelp", ["boucherie", "Suzette, Vaucluse"], [], ""))
        reqs.append(Request(user, "yelp", [DETAILS + " 1", NO_LIMIT_CHAR], [], ""))
        for r in reqs:
            logging.info("Checking a request [%s]" % r)
            a = self.answer(r, {})
            if a:
                logging.info(a + "\n")
            if not(likelyCorrect(a)):
                return False
        return True

    def help(self):
        return("Tapez 'yelp; type; lieux' pour rechercher tous les commerces "
               "de type 'type' autour de 'lieux' classés par note (exemple: 'yelp; indien; Gare du Nord, Paris'). "
               "Si vous voulez lire plus de détails sur le 'n'-ème commerce mentionné par la réponse à votre dernière requête, "
               "tapez 'yelp; details 'n' (exemple: 'yelp; details 2'. "
               "Vous pouvez forcer webtext à afficher les reviews en entier avec l'argument: '%s'." % NO_LIMIT_CHAR)
    
bYelp = BackendYelp()


# 6951
# 7932
# 1830 fichiers 
# 29.6 GO

# Sort mode: 0=Best matched (default), 1=Distance, 2=Highest Rated. If the mode is 1 or 2 a search may retrieve an additional 20 businesses past the initial limit of the first 20 results. This is done by specifying an offset and limit of 20. Sort by distance is only supported for a location or geographic search. The rating sort is not strictly sorted by the rating value, but by an adjusted rating value that takes into account the number of ratings, similar to a bayesian average. This is so a business with 1 rating of 5 stars doesn’t immediately jump to the top.
