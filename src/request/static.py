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

""" Static data. """

########### REQUESTS ############
# Navigation
NEXT="plus"                     # command for one more store message
ALL="tout"                      # command for all stored messages
CLEAR="reset"                   # command for erasing all stored messages
# Syntax
SEP_REQ = "||"                  # separation between different requests
SEP_OPTION = "|"                # separations between arguments and options
# Options
FORWARD = "transfert"
COPY = "copie"
# Backends names
BANK="banque"
BIKES="velo"
WIKI="wiki"
MOVIES="cine"
FORECASTS="meteo"
TRAFIC="trafic"
HELP = "aide"
# Help messages
HELPMESS = (
    "Voici comment écrire vos requêtes:"
    "'" + BIKES + " [lieux]' pour les velibs autour de [lieux]; "
    "'" + TRAFIC + " pour récup. les perturbations RATP; "
    "'" + WIKI + " [requete] pour la page wikipedia contenant'requete', renvoie un résumé (argument optio. pour la langue:fr ou en); "
    "'" + FORECASTS + " [code postal]' pour la météo dans [code postal]; "
    "'" + MOVIES + " [nom] ; [code postal]' pour les séances de ciné des films "
    "contenant [nom] dans [code postal]; "
    "'" + BANK + " pour le montant de mes comptes. "
    " Pour l'aide complète d'un type de requête, envoyer 'aide [requete]'"
    )

############## OTHER STUFF ##############
# 611 the the greatest nb. of car. that a multiple SMS can contain
MAX_CH = 611
adminEmail = "lucca.hirschi@gmail.com"
