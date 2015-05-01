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


# Two types of requests:
#   - 1: 'yelp; type; lieux' avec [type] pour le type de commerce et [lieux] une adresse, ville, métro, etc.
#   - 2: 'yelp; details i' pour avoir le détail du commerce numéro [i] de la dernière requête de type 1 ou 2
#  ----> demande de gérer la DB avec des lignes de types::
#   User - id de requête ou requête RAW - commerce ID - nom du commerce (affichée dans la requête de type 1 ou 2)
# EXAMPLE OF USES:
        # yelp_api.search_query(term='ice cream', location='Paris, France', sort=2, limit=5)
        # yelp_api.search_query(term='ice cream', location='austin, tx', sort=2, limit=5)
        # yelp_api.search_query(category_filter='bikerentals', bounds='37.678799,-123.125740|37.832371,-122.356979', limit=5)
        # yelp_api.business_query(id='amys-ice-creams-austin-3')

DETAILS = "details"
NO_LIMIT_CHAR = "tout"
NB_BUSI = 10
MAX_CHAR_REVIEW = 100

def listBusinesses(request, typeB, location):
    """ Produce the list of businesses of 'typeB' in 'location' (request of type 1). """
    try:
        dicoBusinesses =  yelp_api.search_query(term=typeB, location=location, sort=2, limit=NB_BUSI)
    except YelpAPI.YelpAPIError as e:
        loging.critical("Erreur YELP grave: " + e)
        return(produceMessBug())
    database.db.storeYelpIDs(request.user, dicoBusinesses)
    if len(dicoBusinesses) == 0:
        return("Yelp n'a pas trouvé de réponses à votre rquête.")
    answ = "Liste: "
    i = 1
    for busi in dicoBusinesses:
        # TODO; check les champs qui pourraient êtres affichées
        answ += ("(%d) %s : %d (%d reviews), %s.\n"
                 % (i,
                    busi['name'],
                    busi['rating'],
                    busi['review_count'],
                    busi['location']['display_address']))
        i += 1
    return(answ)

def detailsBusiness(request, idBusiness, no_limit_char_review=False):
    """ Give detailed information (review, TODO, etc.) about one answer of a specific business. """
    try:
        reqBusiness = yelp_api.business_query(id=idBusiness)
    except YelpAPI.YelpAPIError as e:
        loging.critical("Erreur YELP grave: " + e)
        return(produceMessBug())
    # TODO; check les champs qui pourraient êtres affichées
    answ = ("Détailles du lieux %s. Reviews: " % reqBusiness['name'])
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
        answ += ('Note: %d -- %s\n' % (review['rating'], textReview))
    return(answ)


def likelyCorrect(answer):
    return(False)               # TODO

class BackendYelp(Backend):
    backendName = YELP # defined in static.py
    
    def answer(self, request, config):
        # Identify type of Yelp requests
        args = request.argsList
        fstWord = args[0].split()[0]
        if simplifyText(fstWord) == DETAILS:
            # request of type 2
            if len(args[0].split()) != 2:
                print("Requête mal formée. Rappel: " + self.help())
            else:
                number = int(args[0].split()[1])-1
                dicoBusinesses = database.db.getYelpIDs(request.user, number=NB_BUSI)
                if not(number in range(number)):
                    print("Votre dernière requête ne comportait pas %d réponses. Rappel: " % i + self.help())
                else:
                    business = dicoBusinesses[i]
                    idBusiness = business["id"]
                    if NO_LIMIT_CHAR in map(lambda s:simplifyText(s), args):
                        return(detailsBusiness(request, idBusiness, no_limit_char_review=True))
                    else:
                        return(detailsBusiness(request, idBusiness))
        else:
            # request of type 1
            if len(args) != 2:
                print("Requête mal formée. Rappel: " + self.help())
            else:
                return("Liste: " + listBusinesses(request, args[0],args[1]))

    def test(self, user):
        reqs = []
        reqs += Request(user, "yelp", ["glacier", "75, rue Riquet, Paris"], [], "")
        reqs += Request(user, "yelp", ["indien", "Métro Nation, Paris"], [], "")
        reqs += Request(user, "yelp", [DETAILS + "2"], [], "")
        reqs += Request(user, "yelp", [DETAILS + "1"], [], "")
        reqs += Request(user, "yelp", [DETAILS + "1", NO_LIMIT_CHAR], [], "")
        for r in reqs:
            logging.info("Checking a request [%s]" % r)
            a = self.answer(r, {})
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
