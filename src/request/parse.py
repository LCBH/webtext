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
import database.db

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
    "'" + WIKI + " [requete] pour la page wikipedia contenant'requete', renvoie un résumé (argument optio. pour la langue:fr ou en); "
    "'" + FORECASTS + " [code postal]' pour la météo dans [code postal]; "
    "'" + MOVIES + " [nom] [code postal]' pour les séances de ciné des films "
    "contenant [nom] dans [code postal]; "
    "'" + BANK + " pour le montant de mes comptes. "
    " Pour l'aide complète d'un type de requête, envoyer 'aide [requete]'"
    )

# Global dictionnary containing options (if there is more than 1 request, options of the last one are taking into account)
optionsDict = {}

def parseRequest(SMScontent, user, requestType, requestArguments, is_local, is_testing, config_backends):
    """ Parse a request and returns the expected answer. """
    requestArgumentsStrip = map(lambda s : s.strip(), requestArguments)
    # words of the first argument (needed for bikes for instance)
    if len(requestArguments) > 0:
        wordsFirstArgument = requestArguments[0].split()
    else:
        wordsFirstArguments = []
    # We first deal with backend involving private data (they cannot be executed on the request server)
    # BANK
    if requestType == BANK:
        if is_local:
            if user['login'] == "luccaH":
                if wordsFirstArgument[0].lower().strip() == "details":
                    return(fetch.bankInfo(optionsDict, details=True))
                else:
                    return(fetch.bankInfo(optionsDict))
            else:
                return("Pas de backend banque configuré pour l'utilisateur %s." % user['login'])
        else:
            logging.info("I cannot answer because I am executed on the request server but the data needed are private.")
            return None
    # END of private backends

    if is_local and not(is_testing):
        logging.info("No answer will be produced because the backend we need is not private and so the request server will answer.")
        return None
    # We now deal with backends that can be executed on the request server    
    else:
        # BIKES
        if requestType == BIKES:
            where = requestArguments[0]
            return(fetch.velibParisS(optionsDict, where, config_backends))
        # TRAFIC
        elif requestType == TRAFIC:
            is_metro = ("metro" in requestArgumentsStrip)
            is_rer = ("rer" in requestArgumentsStrip)
            if len(requestArguments) == 0:
                is_metro = True
                is_rer = True
                return(fetch.trafic_ratp(optionsDict, metro=is_metro, rer=is_rer))
        # WIKI
        elif requestType == WIKI:
            if len(requestArguments) > 1:
                if (len(requestArguments) <> 2 or
                    ("fr" <> requestArguments[1].lower.strip()) and "en" <> requestArguments[1].lower().strip()):
                    return ("Usage pour wiki: la requête en premier argument et la langue (fr ou en) en second argument"
                            "(optionnel).")
                else:
                    lang = requestArguments[1].lower().strip()
                    return(fetch.wikiSummary(optionsDict, query=requestArguments[0], language=lang))
            else:
                return(fetch.wikiSummary(optionsDict, query=requestArguments[0]))
        # FORECASTS
        elif requestType == FORECASTS:
            where = requestArguments[0]
            return(fetch.forecasts(optionsDict, where))
        # MOVIES
        elif requestType == MOVIES:
            if len(requestArguments) < 1 or len(requestArguments) > 2:
                return "Usage pour cine: 'cine [titre] ; [zip] ou cine [nom de cinema]'\n"
            elif len(requestArguments) == 1:
                return(fetch.showtimes_theater(requestArguments[0]))
            else:
                movie = requestArguments[0]
                zipcode = requestArguments[1]
            return(fetch.showtimes_zip(movie, zipcode))
        # HELP
        elif requestType == HELP:
            if len(wordsFirstArgument) == 0:
                return(HELPMESS)
            else:
                answer = ("Vous avez demandé de l'aide à propos de %s." % wordsFirstArgument[0])
                return(answer + " Désolé mais l'aide n'est pas encore complète.")
        else:
            extract = ("L'utilisateur %s m'a envoyé le texte %s" % (user['name'], SMScontent))
            answer = ("" +
                      extract +
                      ", malheureusement je n'ai pas compris sa requête. " + HELPMESS
                      )
            return(answer)


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
            logging.info("A request correspond to a shortcut...")
            requestS = matches[0][1]
            answ_req = parseContent(requestS, user, is_local, is_testing)
            if not(answ_req) == None:
                answer += answ_req + "||\n"
        # --- We check wheter the request is actually a navigation command ---
        elif (NEXT == requestStrip) or (ALL == requestStrip) or (CLEAR == requestStrip):
            logging.info("A request correspond to a navigation command...")
            if NEXT == requestStrip:
                return("".join(database.db.popMessage(user))) # TODO
            elif ALL == requestStrip:
                return("|".join(database.db.popMessage(user, number=10000))) # TODO
            elif CLEAR == requestStrip:
                database.db.clearQueue(user)
                return(None)
        # --- Otherwise, the request should ba a truly request for a given backend ---        else:
        if "|" in request:
            options = request.split("|")[1]
            requestCore = request.split("|")[0]
        else:
            options = []
            requestCore = request
        # list of options
        optionsList = map(lambda s : s.strip().lower(), options)
        argumentsList = requestCore.split(";")
        if len(argumentsList[0].split()) > 0:
            # backendName
            requestType = argumentsList[0].split()[0].lower().strip()
            # list of arguments
            requestArguments = [(" ".join(argumentsList[0].split()[1:]))] + argumentsList[1:]
        else:
            # backendName
            requestType = argumentsList[0].lower().strip()
            # list of arguments
            requestArguments = argumentsList[1:]
            # Parsing of options
        optionsDict['all'] = (ALL in optionsList)
        optionsDict['forward'] = (FORWARD in optionsList)
        optionsDict['copy'] = (COPY in optionsList)
        logging.debug("requestType: " + str(requestType) +
                      ", requestArguments: " + str(requestArguments))
        return(parseRequest(SMScontent, user, requestType, requestArguments, is_local, is_testing, config_backends))


MAX_CH = 640
def countCar(mess):
#double: (|^€{}[]~) 
    countDouble = ['(','|','^','€','{','}','[',']','~',')']
    nbDouble = len(filter(lambda c: c in countDouble, mess))
    return(nbDouble + len(mess))

def splitSize(mess, maxSize):
    if countCar(mess) < maxSize:
        return([mess])
    else:
        mod = countCar(mess) % maxSize
        exact = countCar(mess) - mod
        nbPartsExact = exact / maxSize
        listSplit = []
        pos = 0
        pos2 = 0
        for i in range(nbPartsExact):
            while pos2+1 < len(mess) and countCar(mess[pos:pos2+1]) <= maxSize:
                pos2 += 1
            part = mess[pos:pos2]
            listSplit.append(part)
            pos = pos2
        lastPart = mess[pos:]
        if lastPart != "":
            listSplit.append(lastPart)
        return(listSplit)

def produceAnswers(SMScontent, user, config_backends, is_local=False, is_testing=False):
    """ Given a SMS content, it returns the expected answers maybe using multiple SMS. """
    whole_answer = parseContent(SMScontent, user, config_backends, is_local=False, is_testing=False)
    if whole_answer != None and countCar(whole_answer) > MAX_CH:
        splitMaxSize = MAX_CH - (4 + 4 + 1 +1) # pour '[XX/XX] '
        listAnswers = splitSize(whole_answer, splitMaxSize)
        logging.info("The answers requires multiple SMS: nb=%d." % len(listAnswers))
        logging.info(str(listAnswers))
        listAnswersFormat = []
        for nb in range(len(listAnswers)):
            answer = listAnswers[nb]
            answerFormat = ("[" + str(nb+1) + "/" + str(len(listAnswers)) + "] ") + answer
            listAnswersFormat.append(answerFormat)
        if optionsDict['all']:
            return(listAnswersFormat, optionsDict)
        else:
            toSend = listAnswersFormat[0]
            toStore = listAnswersFormat[1:]
            database.db.pushMessage(user, toStore)
            return(toSend, optionsDict)
    else:
        if whole_answer == None:
            return(["Error"], optionsDict)
        else:
            return([whole_answer], optionsDict)
