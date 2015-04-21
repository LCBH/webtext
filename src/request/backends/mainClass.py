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

""" Generic classes and methods for backends. """

import os
from os.path import expanduser

from request import *

# -- Static data (install). --
REQUEST_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(REQUEST_DIR) + "/../../"
# -- User Data --
# if os.path.isfile(PROJECT_DIR+'config_backends.py'):
execfile(expanduser(PROJECT_DIR+'config_backends.py'))
user1 = [ u for u in CONF['users'] if u['login'] == 'luccaH'][0]
user2 = [ u for u in CONF['users'] if u['login'] == 'vincentCA'][0]

class IterRegistry(type):
    def __iter__(cls):
        return iter(cls._registry)

class Backend(object):
    __metaclass__ = IterRegistry
    _registry = []
    backendName = ""

    def __init__(self, is_private=False):
        # this is for keeping all availabe backends together and for
        # beeing able to iterating over all of them
        self._registry.append(self)
        self.name = self.backendName
        self.is_private = is_private

    def __str__(self):
        return("BackendName: " + self.backendName)

    def isRequested(self, request):
        """ Is this backend the one requested by request? """
        return (request.backend.strip().lower() == self.name)

    def answerCommon(self, request, config):
        """ Basically call 'answer' after performing uniform checks."""
        if config['is_local'] and not(self.is_private) and not(config['is_testing']):
            logging.info("I won't process this request as the request's server does so.")
        else:
            return(self.answer(request, config))

    # Each sub-backend should implement its own 'answer' method
    def answer(self, request, config):
        """ Parse a request (instance of class Request) and produce the 
        expected answer (in Unicode). """
        raise NotImplementedError

    # Each sub-backend should implement its own 'help' method
    def help(self):
        """ Returns a help message explaining how to use this backend 
        (in Unicode). """
        raise NotImplementedError

    # Each sub-backend should implement its own 'test' method
    def test(self,user):
        """ Test the backend by inputting different requests and check
        the produced answer. Log everything and returns a boolean denoting
        whether the backend is broken or not (False when broken)."""
        raise NotImplementedError
