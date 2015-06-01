# Install gammu
sudo apt-get install gammu gammu-smsd
sudo apt-get install screen
#Config Gammu
cp config_gammu.txt /etc/gammu-smsdrc
# Set up databases
mkdir data
mkdir data/log
mkdir data/SMS
mkdir data/SMS/inbox
mkdir data/SMS/error
mkdir data/SMS/sent
mkdir data/SMS/outbox
chown gammu -R data
#Set up sendSMS.php script
sudo apt-get install apache2 php5 libapache2-mod-php5 -y
# -> enable SSL (should answer to HTTPS requests)
#    (see e.g., http://en.wikibooks.org/wiki/Apache/SSL)
echo "You need the Perl lib: URI::Escape."
echo "Add this to your visudo: '%www-data ALL=(ALL) NOPASSWD: /usr/bin/python /home/lutcheti/webtext/src/rasp/sendSMS.sh'"
# see e.g., http://www.question-defense.com/2010/01/28/perl-module-error-cant-locate-uriescape-pm-in-inc
sudo mkdir /var/www/webtext
sudo mkdir /var/www/webtext/api
sudo chgrp www-data -R /var/www/webtext
sudo cp src/rasp/sendSMS.php /var/www/webtext/api/
sudo chmod u+x /var/www/webtext/api/sendSMS.php

# Need the URI::Escape Lib of Perl (to URLEncode SMS's text before using curl)
# ADD ton crontab (send 1 SMS per month to avoid to get the line closed):
# 0 0 1 * * §home/lutcheti/webtext/src/rasp/send_sms.sh
echo "Launch the gammu-smsd daemon: 'screen -S GAMMU sudo gammu-smsd -c /etc/gammu-smsdrc'."

echo "Now, you must launch ./install_request.sh... "