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
import unicodedata

import fetch
import database.db
from static import *
from backends.main import Backend
from request import Request

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

# Global dictionnary containing options (if there is more than 1 request, options of later requests override previous ones)
optionsDict = {}

def simplifyText(s):
    """Remove extra blanks, replace uppercase letters by lowercase letters and remove all accents from 's'."""
    s1 = unicode(s.strip().lower(), 'utf-8')
    s2 = unicodedata.normalize('NFD', s1).encode('ascii', 'ignore')     
    return(s2)

def parseRequest(request, user, is_local, is_testing, config_backends):
    """ Parse a request (i.e., instance of class Request) and returns the expected answer. """
    request.argsListStrip = map(lambda s : s.strip(), request.argsList)
    # words of the first argument (needed for bikes for instance)
    if len(request.argsList) > 0:
        wordsFirstArgument = request.argsList[0].split()
    else:
        wordsFirstArgument = []
    config = {}
    config['is_local'] = is_local
    config['is_testing'] = is_testing
    config['config_backends'] = config_backends

    # We iterate over all existing backeds and check if backendName matches
    for backend in Backend:
        if backend.isRequested(request):
            logging.info("Backend '%s' handles the request." % backend.name)
            return(backend.answerCommon(request, config))

    # If no backend handled the request and we are not in local, maybe we should print some help message
    if not(is_local) or is_testing:
        print(request.backend)
        if request.backend == HELP:
            if len(request.argsList) > 0:
                for backend in Backend:
                    if backend.backendName == request.argsList[0].lower().strip():
                        logging.info("Help message of Backend '%s' is requested." % backend.name)
                        return(backend.help())
            else:
                return(HELPMESS)
        # If the request if not of the form: "HELP; backend" then we can print some error message
        extract = ("L'utilisateur %s m'a envoyé le texte %s" % (user['name'], request.raw))
        answer = (extract + 
                  ", malheureusement je n'ai pas compris sa requête. " +
                  HELPMESS)
        return(answer)
    else:
        return None

# Parse the inputted text and output the corresponding answer
def parseContent(SMScontent, user, config_backends, is_local, is_testing):
    """ Parse the SMS and produce the list of required answers."""
    # --- We extract the list of requests ---
    listRequests = SMScontent.split(SEP_REQ)
    answer = []
    for request in listRequests:
        requestStrip = request.strip()
        requestStripLower = requestStrip.lower()
        # --- We check whether the request is actually a shortcut ---
        matches = [u for u in user['shortcuts'] if u[0] == requestStrip]
        if len(matches) > 0:
            logging.info("A request correspond to a shortcut...")
            requestS = matches[0][1]
            answ_req = parseContent(requestS, user, config_backends, is_local, is_testing)
            if not(answ_req) == None:
                answer += answ_req
        # --- We check wheter the request is actually a navigation command ---
        elif (NEXT == requestStripLower) or (ALL == requestStripLower) or (CLEAR == requestStripLower):
            logging.info("A request correspond to a navigation command...")
            if is_local:
                logging.info("I won't process this kind of request in local ...")
                return(None)
            else:
                if NEXT == requestStripLower:
                    return(NEXT.title() + ": " + ("".join(database.db.popMessage(user)))) # TODO
                elif ALL == requestStripLower:
                    return(ALL.title() + ": " + (" | ".join(database.db.popMessage(user, number=10000)))) # TODO
                elif CLEAR == requestStripLower:
                    database.db.clearQueue(user)
                    return(CLEAR.title() + ": fait.")
        # --- Otherwise, the request should be a truly request for a given backend ---
        if SEP_OPTION in request:
            options = request.split(SEP_OPTION)[1]
            requestCore = request.split(SEP_OPTION)[0]
        else:
            options = []
            requestCore = request
        # list of options
        optionsList = map(lambda s : s.strip().lower(), options)
        # list of arguments
        argumentsList = requestCore.split(";")
        if len(argumentsList[0].split()) > 0:  # Ex. cine mommy; 75020
            # backendNameRaw
            backendNameRaw = argumentsList[0].split()[0].lower().strip()
            # list of arguments
            argumentsList = ([(" ".join(argumentsList[0].split()[1:]))] +
                             argumentsList[1:]) # X[1:] empty if X contains 1 el.
        else:                                  # Ex. cine; mommy; 75020
            # backendNameRaw
            backendNameRaw = argumentsList[0].lower().strip()
            # list of arguments
            argumentsList = argumentsList[1:]    # X[1:] empty if X contains 1 el.
        backendName = simplifyText(str(backendNameRaw))
        argumentsList = [el.strip() for el in argumentsList if el.strip() != ""] 
        # Parsing of options (need to change global values of optionsDict)
        optionsDict['all'] = (ALL in optionsList)
        optionsDict['forward'] = (FORWARD in optionsList)
        optionsDict['copy'] = (COPY in optionsList)
        request = Request(user, backendName, argumentsList, optionsList, requestCore)
        logging.debug(str(request))
        return(parseRequest(request, user, is_local, is_testing, config_backends))
                          
def countChar(mess):
    """ Count the number of characters counting double for special ones."""
# those car. count double: (|^€{}[]~) 
    countDouble = ['(','|','^','€','{','}','[',']','~',')']
    nbDouble = len(filter(lambda c: c in countDouble, mess))
    return(nbDouble + len(mess))

def splitSize(mess, maxSize):
    """ Split a message into a list of messages not too long for one text."""
    if countChar(mess) < maxSize:
        return([mess])
    else:
        mod = countChar(mess) % maxSize
        exact = countChar(mess) - mod
        nbPartsExact = exact / maxSize
        listSplit = []
        pos = 0
        pos2 = 0
        for i in range(nbPartsExact):
            while pos2+1 < len(mess) and countChar(mess[pos:pos2+1]) <= maxSize:
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
    whole_answer = parseContent(SMScontent, user, config_backends, is_local, is_testing)
    if whole_answer == None or whole_answer.strip() == "":
        return None
    if countChar(whole_answer) > MAX_CH:
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
            return([toSend], optionsDict)
    else:
        return([whole_answer], optionsDict)
