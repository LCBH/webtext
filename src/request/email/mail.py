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
import smtplib



# -- Setup Logging --
logging = logging.getLogger(__name__)

# BEGIN
fromMy = 'webtext.webtext@yahoo.com' # fun-fact: from is a keyword in python, you can't use it as variable, did abyone check if this code even works?
to  = 'lucca.hirschi@gmail.com'
subj='Subject'
date='2/1/2014'
message_text='Hello Or any thing you want to send'
msg = "From: %s\nTo: %s\nSubject: %s\nDate: %s\n\n%s" % ( fromMy, to, subj, date, message_text )
username = str('webtext.webtext@yahoo.com')  
password = str('23b18b8a')  
try :
    server = smtplib.SMTP("smtp.mail.yahoo.com",587)
    server.login(username,password)
    server.sendmail(fromMy, to,msg)
    server.quit()    
    print 'ok the email has sent '
except :
    print 'can\'t send the Email'
# END
