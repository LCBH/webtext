# On a Raspberry Pi (branch rasp), install: #
############################################
# Automatic script: install_rasp.sh
# Install Gammu & its deamon
sudo apt-get install gammu
sudo apt-get install gammu-smsd

# Configure your 3G dongle: type ''dmesg''
and look for your dongle and its port (usually
ttyUSB0, ttyUSB1, ...). Use this to complete the
config file (port and pin).


# On the other server (branch request), install the followings: #
#################################################################
# Automatic script: install_request.sh
# Install Weboob (http://weboob.org/install)
sudo apt-get install weboob