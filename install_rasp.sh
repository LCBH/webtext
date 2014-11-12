cp config_gammu.txt /etc/gammu-smsdrc
mkdir /data
mkdir data/log
mkdir data/SMS
mkdir data/SMS/inbox
mkdir data/SMS/error
mkdir data/SMS/sent
mkdir data/SMS/outbox
chown gammu -R data

# ADD ton crontab (send 1 SMS per month to avoid to get the line closed):
# 0 0 1 * * §home/lutcheti/webtext/src/rasp/send_sms.sh