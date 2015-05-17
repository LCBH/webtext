#Config Gammu
cp config_gammu.txt /etc/gammu-smsdrc
# Set up databases
mkdir /data
mkdir data/log
mkdir data/SMS
mkdir data/SMS/inbox
mkdir data/SMS/error
mkdir data/SMS/sent
mkdir data/SMS/outbox
chown gammu -R data
#Set up sendSMS.php script
sudo apt-get install apache2
# -> enable SSL (should answer to HTTPS requests)
sudo mkdir /var/www/webtext
sudo mkdir /var/www/webtext/api
sudo chgrp www-data -R /var/www/webtext
sudo cp src/rasp/sendSMS.php /var/www/webtext/api/
sudo chmod u+x /var/www/webtext/api/sendSMS.php

# Need the URI::Escape Lib of Perl (to URLEncode SMS's text before using curl)
# ADD ton crontab (send 1 SMS per month to avoid to get the line closed):
# 0 0 1 * * §home/lutcheti/webtext/src/rasp/send_sms.sh
