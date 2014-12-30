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
import database

# -- Setup Logging --
logging = logging.getLogger(__name__)

# -- Requests --
# Each received SMS is interpreted either as a (i) navigation command, as a (ii) request for a backend.
# (ii) Requests are of the form:
#         [backendName] [arg1] ; [arg2] ; [...] ; [argn] | [option1] [option2] [option3]
#    It is also possible to make a bunch of requests at once using
#         [request1] || [request2] || [..] || [requestn]
#    - backendName is the type of request or a shorcut defined by the user. Currently we support the following backends:
#      'banque', 'velo', 'wiki', 'cine' and 'trafic';
#    - arguments can be strings (e.g., movie or location), numbers (e.g. zipcode or hour) etc. ;
#    - options are optional and allow to precise how the answer will be delivered. We support this list of options:
#        . 'all': if the answer is long and multiple SMSs are needed, we will receive them all;
#        . 'transfer [number]' sends the answer to [number] instead of to you;
#        . 'copy [number]' sends the answer both to you and to [number].
# (i) Navigation commands can be used after sending a request.:
#    - 'plus' will send you one more SMS containing the rest of the answer of the previous request you made;
#    - 'plus [number]' will send you [number] more SMS containing the remaining of the answer of the previous request you made;
#    - 'all' will send you [number] all remaining SMSs of the answer of the previous request you made.
#    - 'reset' will reset the queue of remaining SMSs.
# Navigation
NEXT="plus"
ALL="tout"
CLEAR="reset"
# Options
FORWARD = "transfert"
COPY = "copie"
# Backends
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
    "'" + TRAFIC + " pour récup. les perturbations RATP; "
    "'" + WIKI + " [requete] pour la page wikipe. de 'requete' et renvoie un résumé (argument optio. pour la langue:fr ou en); "
    "'" + FORECASTS + " [code postal]' pour la météo dans [code postal]; "
    "'" + MOVIES + " [nom] [code postal]' pour les séances de cinéma des films "
    "contenant [nom] dans [code postal]; "
    "'" + BANK + " pour récupérer le montant de mes comptes. "
    " Pour avoir l'aide complète d'un type de requête, envoyer 'aide [requete]' "
    "(par exemple 'help cine').")

# Parse the inputted text and output the corresponding answer
def parseContent(SMScontent, user, config_backends, is_local=False, is_testing=False):
    """ Parse the SMS and produce the required answer. """
    # --- We extract the list of requests ---
    listRequests = SMScontent.split("||")
    answer = ""
    for request in listRequests:
        requestStrip = request.strip()
        # --- We check whether the request is actually a shortcut ---
        matches = [u for u in user['shortcuts'] if u[0] == requestStrip]
        if len(matches) > 0:
            requestS = matches[0][1]
            answ_req = parseContent(requestS, user, is_local, is_testing)
            if not(answ_req) == None:
                answer += answ_req + "||\n"
        # --- We check wheter the request is actually a navigation command ---
        elif (NEXT == requestStrip) or (ALL == requestStrip) or (CLEAR == requestStrip):
            if NEXT == requestStrip:
                return(database.db.popMessage()) # TODO: qd on push des messages, ne pas oublier d'ajouter [2/3] au début par exemple.
            elif ALL == requestStrip:
                pass
            elif CLEAR == requestStrip:
                pass
        # --- Otherwise, the request should ba a truly request for a given backend ---
        else:
            if "|" in request:
                options = request.split("|")[1]
                requestCore = request.split("|")[0]
            else:
                options = []
                requestCore = request
            # list of options
            optionsList = map(lambda s : s.strip().lower(), options)
            argumentsList = requestCore.split(";")
            # backendName
            requestType = argumentsList[0].lower().strip()
            # list of arguments
            requestArguments = argumentsList[1:]
            requestArgumentsStrip = map(lambda s : s.strip(), requestArguments)
            # words of the first argument (needed for bikes for instance)
            if len(requestArguments) > 0:
                wordsFirstArgument = requestArguments[0].split()
            else:
                wordsFirstArguments = []
            # Parsing of options
            options = {}
            options['all'] = (ALL in optionsList)
            options['forward'] = (FORWARD in optionsList)
            options['copy'] = (COPY in optionsList)
            # We first deal with backends that can be executed only in local
            # BANK
            if requestType == BANK:
                if is_local:
                    if user['login'] == "luccaH":
                        if wordsFirstArgument[0].lower().strip() == "details":
                            return(fetch.bankInfo(options, details=True))
                        else:
                            return(fetch.bankInfo(options))
                    else:
                        return("Pas de backend banque configuré pour l'utilisateur %s." % user['login'])
                else:
                    logging.info("Je ne vais pas répondre à la requête car je ne suis pas exécuté en local"
                                 "et les données demandées sont privées.")
                    return None
            # Now, we deal with all others backends
            if is_local and not(is_testing):
                logging.info("Je ne vais pas répondre à la requête car je suis éxécuté en local"
                             "et les données demandées ne sont privées.")
                return None
            else:
                # BIKES
                if requestType == BIKES:
                    where = requestArguments[0]
                    return(fetch.velibParisS(options, where, config_backends))
                # TRAFIC
                elif requestType == TRAFIC:
                    is_metro = ("metro" in requestArgumentsStrip)
                    is_rer = ("rer" in requestArgumentsStrip)
                    if len(requestArguments) == 0:
                        is_metro = True
                        is_rer = True
                    return(fetch.trafic_ratp(options, metro=is_metro, rer=is_rer))
                # WIKI
                elif requestType == WIKI:
                    if len(requestArguments) > 1:
                        if (len(requestArguments) <> 2 or
                            ("fr" <> requestArguments[1].lower.strip()) and "en" <> requestArguments[1].lower().strip()):
                            return ("Usage pour wiki: la requête en premier argument et la langue (fr ou en) en second argument"
                                    "(optionnel).")
                        else:
                            lang = requestArguments[1].lower().strip()
                            return(fetch.wikiSummary(query=requestArguments[0], language=lang))
                    else:
                        return(fetch.wikiSummary(query=requestArguments[0]))
                # FORECASTS
                elif requestType == FORECASTS:
                    where = requestArguments[0]
                    return(fetch.forecasts(where))
                # MOVIES
                elif requestType == MOVIES:
                    if len(wordsFirstArgument) < 2:
                        return "Usage pour cine: 'cine [titre] [zip]'\n"
                    movie = " ".join(wordsFirstArgument[0:-1])
                    zipcode = wordsFirstArgument[-1]
                    return(fetch.showtimes_zip(movie, zipcode))
                # HELP
                elif requestType == HELP:
                    if len(wordsFirstArgument) == 0:
                        return(HELPMESS)
                    else:
                        answer = ("Vous avez demandé de l'aide à propos de %s." % wordsFirstArgument[0])
                        return(answer + " Désolé mais l'aide n'est pas encore complète.")
                else:
                    extract = ("L'utilisateur %s (numéro: %s) m'a envoyé le texte %s" % (user['name'], user['number'], SMScontent))
                    answer = ("Bonjour, je suis la Raspberry Pi et j'ai un problème. " +
                              extract +
                              ", malheureusement je n'ai pas compris sa requête. " + HELPMESS
                              )
                    return(answer)
