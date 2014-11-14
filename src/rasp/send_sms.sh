# This script sends a SMS from the RaspBerry Pi's SIM card
# to be executed once a month
cd /home/lutcheti/webtext/data/SMS/outbox
sudo gammu-smsd-inject -c /etc/gammu-smsdrc TEXT 0632368091 -text "Coucou c'est la RaspBerry Pi. Je t'envoie mon SMS mensuel."