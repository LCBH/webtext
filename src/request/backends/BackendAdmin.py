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

import logging
import subprocess

from static import *
from utils import *
from mainClass import *

# -- Setup Logging --
logging = logging.getLogger(__name__)

def likelyCorrect(a):
    return(a and len(a) > 10)

class BackendAdmin(Backend):
    backendName = "admin"

    def answer(self, request, config):
        arg1 = request.argsList[0]
        arg2 = None if len(request.argsList) < 2 else request.argsList[1].split()[1]
        if simplifyText(arg1) == "log":
            answ = "Log: "
            if arg2:
                maxi = int(arg2)
            else:
                maxi = 5
            bashCommandList = ("tail -n %d ./../../data/log/handleSMS.log" % maxi)
            logging.info("Before subprocess: %s" % bashCommandList)
            try:
                process = subprocess.Popen(bashCommandList.split(), stdout=subprocess.PIPE)
            except OSError as e:
                logging.error("admin > Popen | Execution failed:" + str(e))
                return(MESS_BUG())
            output = process.communicate()[0]
            listLines = output.splitlines()
            listLines.reverse()
            answ += "\n".join(listLines[0:maxi])
            return(answ)
        if simplifyText(arg1) == "test":
            answ = "Test: "
            bashCommandList = ("python test.py backendsNotAdmin")
            logging.info("Before subprocess: %s" % bashCommandList)
            try:
                process = subprocess.Popen(bashCommandList.split(),
                                           stdout=subprocess.PIPE)
            except OSError as e:
                logging.error("admin > Popen | Execution failed:" + str(e))
                return(MESS_BUG())
            output = process.communicate()[0]
            listLines = output.splitlines()
            res = "\n".join(listLines)
            answ += str(res.split("Backend passes all tests.\n")[1])
            return(answ)

    def test(self, user):
        reqs = []
        reqs.append(Request(user, "admin", ["log", "size 100"], [], ""))
        reqs.append(Request(user, "admin", ["log"], [], ""))
        reqs.append(Request(user, "admin", ["test"], [], ""))
        for r in reqs:
            logging.info("Checking a request [%s]" % r)
            a = self.answer(r, {})
            if a:
                logging.info(a + "\n")
            if not(likelyCorrect(a)):
                return False
        return True

        
    def help(self):
        return(
            "'admin; log; [n]' for the log truncated after [n] lines (this is optional). "
            "'admin; test' to launch a test over all backends (except [admin]). "
            )

bAdmin = BackendAdmin()
