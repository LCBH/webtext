# to do before using the "request server"
# Tools for Weboob
sudo aptitude install python-html2text python-mechanize libyaml-0-2 python2.7-simplejson python-setuptools pyqt4-dev-tools python-dev libxml2-dev libxslt1-dev python-prettytable zlib1g-dev
# Weboob
sudo aptitude install weboob
# PHP
sudo aptitude install php5 
sudo aptitude install curl libcurl3 php5-curl

mkdir src/request/tmp
mkdir data
mkdir data/log
mkdir data/database
mkdir data/backends
mkdir src/request/tmpsudo


# for the webtext's API
sudo mkdir /var/www/webtext
sudo mkdir /var/www/webtext/api
sudo chgrp www-data -R /var/www/webtext
sudo cp src/request/sms.php /var/www/webtext/api/
sudo cp src/request/nexmo.php /var/www/webtext/api/
sudo chmod u+x /var/www/webtext/api/sms.php
sudo chmod u+x /var/www/webtext/api/nexmo.php


# Python modules
wget https://bootstrap.pypa.io/ez_setup.py -O - | sudo python
sudo easy_install wget
sudo easy_install dataset
sudo easy_install wikipedia
sudo easy_install yelpapi
