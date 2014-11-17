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

import logging
import fetch

# -- Setup Logging --
logging = logging.getLogger(__name__)

# Requests
BANK="banque"
BIKES="velo"
MOVIES="cine"
FORECASTS="meteo"
HELP = ("Voici comment écrire vos requêtes:"
        "'" + BIKES + " [lieux]' pour les velibs autour de [lieux]; "
        "'" + MOVIES + " [nom] [code postal]' pour les séances de cinéma des films "
        "contenant [nom] dans [code postal]; "
        "'" + FORECASTS + " [code postal]' pour la météo dans [code postal]; "
        "'" + BANK + " pour récupérer le montant de mes comptes. "
        " Pour avoir l'aide complète d'un type de requête, envoyer 'help [requete]' "
        "(par exemple 'help cine').")

# Parse the inputted text and output the corresponding answer
def parseContent(SMScontent, user, is_local=False, is_testing=False):
    # TODO: define a common structure for requests ["backend request args] ?
    # extract word per word the request
    # We start with the case: should be executed in local
    words = SMScontent.split()
    requestType = words[0].lower()
    requestContent = words[1:]
    if requestType == BANK:
        if is_local:
            if requestContent[0].lower() == "details":
                return(fetch.bankInfo(True))
            else:
                return(fetch.bankInfo())
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
            return(fetch.velibParis(where))
        elif requestType == FORECASTS:
            where = requestContent[0]
            return(fetch.forecasts(where))
        elif requestType == MOVIES:
            if len(requestContent) < 3:
                return "Usage pour cine: 'cine [titre] [zip]'\n"
            movie = " ".join(requestContent[0:-1])
            zipcode = requestContent[-1:]
            return(fetch.showtimes_zip(movie, zipcode))
        else:
            extract = ("L'utilisateur %s (numéro: %s) m'a envoyé le texte %s" % (user['name'], user['number'], SMScontent))
            answer = ("Bonjour, je suis la Raspberry Pi et j'ai un problème. " +
                      extract +
                      ", malheureusement je n'ai pas compris sa requête. " + HELP
                      )
            return(answer)
