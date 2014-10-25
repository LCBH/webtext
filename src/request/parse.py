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

import fetch

# Parse the inputted text and output the corresponding answer
def parseContent(text):
    logging.info("Starting parseContent")
    if text == "banque":
        return(fetch.bankInfo())
    elif text == "banque details":
        return(fetch.bankInfo(True))
    elif text[:4] == "velo":
        if text == "velo":
            where = "chapelle"
        elif text == "velo moi":
            where = "riquet"
        else:
            where = text[5:]
        fetch.velibParis(where)
    else:
        extract = ('Le numéro %s ma envoyé le texte %s' % (SMSnumber, SMScontent))
        answer = ("Bonjour, je suis la Raspberry Pi et j'ai un problème. " +
                  extract +
                  ", malheuresement je n'ai pas compris sa requête.")
        return(answer)
