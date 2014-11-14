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

# Parse the inputted text and output the corresponding answer
def parseContent(SMScontent, user, is_local=False):
    # TODO: define a common structure for requests ["backend request args] ?
    # extract word per word the request
    if SMScontent == "banque":
        if is_local:
            return(fetch.bankInfo())
        else:
            logging.info("Je ne vais pas répondre à la requête car je ne suis pas exécuté en local"
                         "et les données demandées sont privées.")
            return None
    elif SMScontent == "banque details":
        return(fetch.bankInfo(True))
    elif SMScontent[:4] == "velo":
        if SMScontent == "velo":
            where = "chapelle"
        elif SMScontent == "velo moi":
            where = "riquet"
        else:
            where = SMScontent[5:]
        return(fetch.velibParis(where))
    elif SMScontent[:4] == "cine":
        mess = SMScontent.split()
        if len(mess) < 3:
            return "Usage pour cine: 'cine [titre] [zip]'\n"
        movie = " ".join(mess[1:-1])
        zipcode = mess[-1:]
        return(fetch.showtimes_zip(movie, zipcode))
    else:
        extract = ("L'utilisateur %s (numéro: %s) m'a envoyé le texte %s" % (user['name'], user['number'], SMScontent))
        answer = ("Bonjour, je suis la Raspberry Pi et j'ai un problème. " +
                  extract +
                  ", malheureusement je n'ai pas compris sa requête." +
                  "TODO: afficher l'aide.")
        return(answer)
