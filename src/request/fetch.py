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

""" Fetch different types of information using Weboob and some APIs and pretty
format as a SMS' text."""

import os
import sys
import wget                     # wget command (for api free)
import subprocess               # for launching bash programs
import urllib                   # used to transform text into url
import logging
from os.path import expanduser
import backends.allocine

# -- Static data (install). --
REQUEST_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(REQUEST_DIR) + "/../"
LOG_DIR = PROJECT_DIR + "data/log/"
# -- User Data --
if os.path.isfile(PROJECT_DIR+'config_backends.txt'):
    execfile(expanduser(PROJECT_DIR+'config_backends.txt'))
# -- Setup Logging ''
logging.basicConfig(filename=LOG_DIR + 'handleSMS.log',
                    level=logging.DEBUG,
                    format='%(asctime)s|%(levelname)s|fetch:%(message)s',
                    datefmt='%d/%m %I:%M:%S %p')


def bankInfo(details=False):
    """ Fetch the amounts of bank accounts."""
    logging.info("Starting bankInfo")
    bashCommandList = "boobank list --formatter=multiline --select=label,balance"
    bashCommandHistory = ("boobank history 102780735700020237601EUR@creditmutuel "
                          "--formatter=multiline --select=date,raw,amount")
    logging.info("Before subprocess: %s" % bashCommandList)
    process = subprocess.Popen(bashCommandList.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]
    if details:
        logging.info("More details needed, before subprocess: %s" % bashCommandHistory)
        process = subprocess.Popen(bashCommandHistory.split(), stdout=subprocess.PIPE)
        outputHistory = process.communicate()[0]
        output = output + "||| Les détails:\n" + str(outputHistory)
    answer = ("J'ai compris que tu voulais un point sur tes comptes:\n" +
              str(output))
    return(answer)

def velibParis(where):
    """ Fetch available stations and bikes around a given location."""
    logging.info("Starting velibParis")
    bashPrefix = "boobsize search "
    # bashPrefix2 = "boobsize last_sensor_measure "
    # prefixBikes = "available_bikes"
    # prefixFree = "available_bike_stands"
    # stationChap = ".18040.Paris.jcvelaux"
    # stationDep = "18110.Paris.jcvelaux"
    # stationRiqet = ".18010.Paris.jcvelaux"
    # stationRiquetP = ".18109.Paris.jcvelaux"
    bashC = bashPrefix + where
    logging.info("Before subprocess: %s." % bashC)
    process = subprocess.Popen(bashC.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]
    # PB: only table formatter shows all required info but not adapted for SMS
    # SOL: truncatated 47 first caracters of all lines
    TRUNC = 51
    output_trunc = ""
    listLines = output.splitlines()[2:] # drop the menu
    for line in listLines:
        if len(line) > 1:
            line = line[TRUNC:]
            output_trunc += line + "\n"
    answer = ("J'ai compris que tu voulais avoir les dispos des vélos à "+where+"."
              " Voici ces infos:\n" +
              str(output_trunc))
    return(answer)

def cinema(request):
    # parse the request: showtimes? search for movies? etc....
    allocine.showtimes("mommy")
    return()
