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

""" Parse a request and using Fetch, return the required answer.
We thus define here the conventions of requests."""

from __future__ import unicode_literals # implicitly declaring all strings as unicode strings

import logging
import fetch


# -- Setup Logging --
logging = logging.getLogger(__name__)

# Requests
BANK="banque"
BIKES="velo"
WIKI="wiki"
MOVIES="cine"
FORECASTS="meteo"
TRAFIC="trafic"
HELP = "aide"
HELPMESS = (
    "Voici comment écrire vos requêtes:"
    "'" + BIKES + " [lieux]' pour les velibs autour de [lieux]; "
    "'" + TRAFIC + " pour connaitre toutes les perturbations du réseau RATP; "
    "'" + WIKI + " [requete] cherche la page wikipedia de 'requete' et renvoie un résumé (ajoutez '; [lang]' pour préciser la langue); "
    "'" + FORECASTS + " [code postal]' pour la météo dans [code postal]; "
    "'" + MOVIES + " [nom] [code postal]' pour les séances de cinéma des films "
    "contenant [nom] dans [code postal]; "
    "'" + BANK + " pour récupérer le montant de mes comptes. "
    " Pour avoir l'aide complète d'un type de requête, envoyer 'aide [requete]' "
    "(par exemple 'help cine').")

# Parse the inputted text and output the corresponding answer
def parseContent(SMScontent, user, config_backends, is_local=False, is_testing=False):
    # TODO: define a common structure for requests ["backend request args] ?
    # extract word per word the request
    # We start with the case: should be executed in local
    # Search for a shortcut:
    matches = [u for u in user['shortcuts'] if u[0] == SMScontent]
    if len(matches) > 0:
        answer = ""
        for requ in matches[0][1]:
            answ_req = parseContent(requ, user, is_local, is_testing)
            if not(answ_req) == None:
                answer += answ_req + "|| \n"
        return(answer)
    words = SMScontent.split()
    requestType = words[0].lower()
    requestContent = words[1:]
    if requestType == BANK:
        if is_local:
            if user['login'] == "luccaH":
                if requestContent != [] and requestContent[0].lower() == "details":
                    return(fetch.bankInfo(True))
                else:
                    return(fetch.bankInfo())
            else:
                return("Pas de backend banque configuré pour l'utilisateur %s." % user['login'])
        else:
            logging.info("Je ne vais pas répondre à la requête car je ne suis pas exécuté en local"
                         "et les données demandées sont privées.")
            return None
    # Now, we deal with the case: should be executed in the request server and not in local:   
    if is_local and not(is_testing):
        logging.info("Je ne vais pas répondre à la requête car je suis éxécuté en local"
                     "et les données demandées ne sont privées.")
        return None
    else:
        if requestType == BIKES:
            where = ' '.join(requestContent)
            return(fetch.velibParisS(where, config_backends))
        elif requestType == TRAFIC:
            return(fetch.trafic_ratp(metro=True, rer=True))
        elif requestType == WIKI:
            if ";" in requestContent:
                lang = requestContent[-1]
                query = ' '.join(requestContent[0:-2])
                return(fetch.wikiSummary(query=query, language=lang))
            else:
                query = ' '.join(requestContent)
                return(fetch.wikiSummary(query))
        elif requestType == FORECASTS:
            where = requestContent[0]
            return(fetch.forecasts(where))
        elif requestType == MOVIES:
            if len(requestContent) < 3:
                return "Usage pour cine: 'cine [titre] [zip]'\n"
            movie = " ".join(requestContent[0:-1])
            zipcode = requestContent[-1:]
            return(fetch.showtimes_zip(movie, zipcode))
        elif requestType == HELP:
            if len(requestContent) == 0:
                return(HELPMESS)
            else:
                answer = ("Vous avez demandé de l'aide à propos de %s." % requestContent[0])
                return(answer + " Désolé mais l'aide n'est pas encore complète.")
        else:
            extract = ("L'utilisateur %s (numéro: %s) m'a envoyé le texte %s" % (user['name'], user['number'], SMScontent))
            answer = ("Bonjour, je suis la Raspberry Pi et j'ai un problème. " +
                      extract +
                      ", malheureusement je n'ai pas compris sa requête. " + HELPMESS
                      )
            return(answer)
