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

""" Helping functions. """

from __future__ import unicode_literals # implicitly declaring all strings as unicode strings
import unicodedata


BLANK = " "

def simplifyText(s):
    """Remove extra blanks (outside), replace uppercase letters by lowercase letters and remove all accents from 's'."""
    s1 = unicode(s.strip().lower(), 'utf-8')
    s2 = unicodedata.normalize('NFD', s1).encode('ascii', 'ignore')     
    return(s2)

def compactText(s):
    """ Remove extra blanks (at most one blank). """
    while (BLANK + BLANK) in s:
        print(s)
        s = s.replace(BLANK + BLANK, BLANK)
    return(s)
