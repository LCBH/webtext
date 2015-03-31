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

""" Generic classes and methods for requests. """

class Request:
    """Based class for requests."""
    def __init__(self, user, backendName, argsList, optionsList, requestCore):
        self.user = user                # dico (bad)
        self.backend = backendName      # UTF8 string
        self.argsList = argsList        # List of UTF8 strings
        self.optionsList = optionsList  # List of UTF8 strings
        self.raw = requestCore  # UTF8 string

    def __str__(self):
        return(("User: %s: / " % self.user["login"]) +
               "BackendName: %s / " % self.backend +
               "ArgsLst: %s / " % str(self.argsList) +
               "OptionList: %s." % str(self.optionsList) +
               "\n")

