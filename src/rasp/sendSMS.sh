# This script sends a SMS from the RaspBerry Pi's SIM card
cd /home/lutcheti/webtext/data/SMS/outbox
sudo gammu-smsd-inject -c /etc/gammu-smsdrc TEXT $1 -text "$2"