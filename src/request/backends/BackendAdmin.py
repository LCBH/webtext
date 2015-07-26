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
# DO NOT import unice_litterals because we only deal with strings here
import logging
import subprocess

from static import *
from utils import *
from mainClass import *

# -- Setup Logging --
logging = logging.getLogger(__name__)

PATH_HERE = os.path.dirname(os.path.abspath(__file__))
PATH_LOG = PATH_HERE + "/../../../data/log/handleSMS.log"
PATH_TESTPY = PATH_HERE + "/../test.py"
nb_my_log = 6      # this is the number of lines that the current request has produced
   # this is dirty way to remove them (has to be tweaked any time we add/rm logging info)

def likelyCorrect(a):
    return(a and len(a) > 10)

# Still a problem (to reproduce: meteo request and then log request) + problem in handleSMS (decode uniode
#cf. file BUG
class BackendAdmin(Backend):
    backendName = "admin"

    def answer(self, request, config):
        arg1 = request.argsList[0]
        arg2 = None if len(request.argsList) < 2 else request.argsList[1].split()[1]
        if simplifyText(arg1) == "log":
            answ = str("Log: ")
            if arg2:
                maxi = int(arg2) + nb_my_log
            else:
                maxi = 5 + nb_my_log
            bashCommandList = ("tail -n %d %s" % (maxi, PATH_LOG))
            logging.info("Before subprocess: %s" % bashCommandList)
            try:
                process = subprocess.Popen(bashCommandList.split(), stdout=subprocess.PIPE)
            except OSError as e:
                logging.error("admin > Popen | Execution failed:" + str(e))
                return(MESS_BUG())
            output = process.communicate()[0]
            listLines = output.splitlines()
            listLines.reverse()
            answ += (str("\n")).join(listLines[nb_my_log:maxi])
            return(answ)
        if simplifyText(arg1) == "test":
            answ = str("Test: ")
            bashCommandList = ("python %s backendsNotAdmin" % PATH_TESTPY)
            logging.info("Before subprocess: %s" % bashCommandList)
            try:
                process = subprocess.Popen(bashCommandList.split(),
                                           stdout=subprocess.PIPE)
            except OSError as e:
                logging.error("admin > Popen | Execution failed:" + str(e))
                return(MESS_BUG())
            output = process.communicate()[0]
            listLines = output.splitlines()
            res = (str("\n")).join(listLines)
            if "Summary of tests:" in res:
                answ += res.split(str("Summary of tests:"))[1]
            else:
                answ += "no results found..."
            return(answ)

    # Warning: 'log' requests cannot be tested easily because when testing, log information is redirected
    def test(self, user):
        reqs = []
        reqs.append(Request(user, "admin", ["log", "size 20"], [], ""))
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
