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
import wikipedia

from mainClass import *
from static import *


# -- Setup Logging --
logging = logging.getLogger(__name__)

CHOSENNUMBER = "numero"
LIST = "liste"
RECHERCHE = "recherche"

def wikiSummary(request):
    """Fetch the summary of Wikipadia's articles. """
    wikipedia.set_lang("fr")    # in French by default

    # -- PARSING --
    searchText = request.argsList[0]
    detailsList = None
    chosenNumber = None
    onlyResearch = None
    # 'LIST' (ask for the list of matched articles)
    if LIST in map(lambda s: s.strip().lower(), request.argsList[1:]):
        detailsList = True
    # 'CHOSENNUMBER i' (ask for the i-nth article of the matched articles)
    if CHOSENNUMBER in map(lambda s: s.strip().lower().split()[0], request.argsList[1:]):
        chosenNumber = int(filter(lambda s: s.strip().lower().split()[0] == "numero", request.argsList[1:])[0].split()[1])
    #'RECHERCHE' (make a research instead of looking for the summary)
    if RECHERCHE in map(lambda s: s.strip().lower(), request.argsList[1:]):
        onlyResearch = True
    # languages: "fr" or "en" for the moment
    if "en" in map(lambda s: s.strip().lower(), request.argsList[1:]):
        wikipedia.set_lang("en")
    if "fr" in map(lambda s: s.strip().lower(), request.argsList[1:]):
        wikipedia.set_lang("fr")

    # -- FECTHING -- 
    max_nb_results = 10
    max_nb_searchs = 20
    options = None
    failSuggest = None
    answ = ""

    if onlyResearch:
        searchs = wikipedia.search(searchText, results = max_nb_searchs)
        answ += ("Voici tous les titres d'articles que l'on a trouvé: [" +
                 ",".join(searchs) + "].")
        return(answ)
    # safe access to the Wiki'API
    try:
        # fails if there is an ambiguity
        try:
            # this does not fail if ther is no ambiguity on the required article
            summary = wikipedia.summary(searchText, auto_suggest = False)
            suggest = wikipedia.suggest(searchText)
            title = suggest if suggest else searchText
        except wikipedia.exceptions.DisambiguationError as e:
            nbOptions = len(e.options)
            options = e.options[:(min(len(e.options), max_nb_results))]
            # there is an ambiguity -> choose the number-nth
            number = chosenNumber if chosenNumber else 1
            if len(options) > number - 1:
                try:
                    newSearchText = options[number - 1]
                    if newSearchText.strip() == searchText.strip() and not(chosenNumber) and len(options) > 1:
                        newSearchText = options[1]
                    summary = wikipedia.summary(newSearchText, auto_suggest = False)
                    title = newSearchText
                # In that case, we failed to disambiguate the request
                except wikipedia.exceptions.DisambiguationError as e:
                    failSuggest = True
#            results = wikipedia.search(searchtext, results=max_nb_results)
    except IOError as e:
        logging.error("wikiSummary > wikipedia.search | I/O error({0}): {1}".format(e.errno, e.strerror))
        return(MESS_BUG())

    # -- ANSWER --
    # Fail to resolve ambiguity
    if failSuggest:
        answ += ("Nous n'avons pas réussi à trouver l'article le plus pertinent parmis cette liste: " +
                 "["  + ", ".join(options) + "]. " +
                 "Vous pouvez maintenant affiner votre recherche.")
        return(answ)
    # No articles matched the request
    if options and (len(options) == 0 or not(len(options) > number - 1)):
        answ += "Aucun article ne correspond à votre requête. Essayez avec une requête plus petite."
        return(answ)
    # Strictly more than 1 article matches the request
    if options and len(options) > 1:
        if detailsList:
            answ += (("%d articles répondent à votre requête. Voici la liste des %d premiers: " % (nbOptions, max_nb_results))
                     + "[" + ", ".join(options) + "]. ")
            if chosenNumber:
                answ += ("Voici le %d-ème: " % chosenNumber)
            else:
                answ += ("Voici le premier: ")
        else:
            if chosenNumber:
                answ += ("%d articles répondent à votre requête. Voici le %d-ème: " % (nbOptions, chosenNumber))
            else:
                answ += ("%d articles répondent à votre requête. Voici le premier: " % nbOptions)
    # Exactly one article matched the request
    else:
        answ += "Voici le seul article qui répond à votre requête: "
    answ += ("[%s] -- " % title) + summary
    return(answ)


def likelyCorrect(a):
    return(("Amboise" in a or "libertin" in a or "commune" in a) or # Bussy
           ("Git" in a and "Ruby" in a) or                          # Github
           ("Battle" in a or "Sunweb-Napoleon" in a) or             # Napoleon
           ("cathédrale" in a))                                     # Sully


class BackendWiki(Backend):
    backendName = WIKI # defined in static.py

    def answer(self, request, config):
        if len(request.argsList) > 0:
            return(wikiSummary(request))
        else:
            return("Vous avez mal tapé votre requête. Rappel: " + self.help())

    def test(self, user):        
        r1 = Request(user, "wiki", ["Bussy"], [], "")
        r2 = Request(user, "wiki", ["Bussy", "liste"], [], "")
        r2 = Request(user, "wiki", ["Bussy", "recherche"], [], "")
        r3 = Request(user, "wiki", ["Bussy", "liste", "numero 3"], [], "")
        r4 = Request(user, "wiki", ["Bussy", "numero 3"], [], "")
        r5 = Request(user, "wiki", ["Bussy", "en"], [], "")
        r6 = Request(user, "wiki", ["Napoleon", "en", "liste"], [], "")
        r7 = Request(user, "wiki", ["Napoleon", "recherche"], [], "")
        r8 = Request(user, "wiki", ["Github", "fr"], [], "")
        r9 = Request(user, "wiki", ["Sully"], [], "")
        for r in [r1,r2,r3,r4,r5, r6, r7, r8, r9]:
            logging.info("Checking a request [%s]" % r)
            a = self.answer(r, {})
            logging.info(a + "\n")
            if not(likelyCorrect(a)):
                return False
        return True

        
    def help(self):
            return("Tapez 'wiki; texte' pour recevoir le résumé du premier article trouvé avec la recherche 'texte'. "
                   " Vous pouvez changer la langue comme ceci: 'wiki; Sully; en' (pour l'anglais). "
                   " Vous pouvez recevoir la liste des autres articles (en cas d'ambiguité) avec l'argument 'liste': "
                   "ex. 'wiki; Sully; liste'. Vous pouvez choisir de recevoir le n-ième de la liste comme ceci: "
                   "'wiki Sully; liste; numero n' ou 'wiki Sully; numero n'. "
                   "Finalement, vous pouvez recherchez tous les titres d'articles se rapprochant de votre texte avec l'option "
                   "'recherche': ex. 'wiki; Napoleon; recherche'.")


bWiki = BackendWiki()
