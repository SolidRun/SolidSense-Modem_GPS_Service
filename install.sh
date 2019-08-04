#!/bin/bash
#
#  script to install modem gps service on solid sense
#

FNAME=Modem_GPS_Service
DIR=/data/solidsense
echo "creating directories"
if [ ! -d $DIR/log ]
then
	mkdir $DIR/log
	chmod 777 $DIR/log
fi
if [ ! -d $DIR/modem_gps ]
then
	mkdir $DIR/modem_gps
	chmod 777 $DIR/modem_gps
fi

echo "installing the packages"
python3 -m pip install pyserial grpcio grpcio-tools
echo "starting the service for modem and GPS"
cp modem_gps.service /etc/systemd/system
chmod 644 /etc/systemd/system/modem_gps.service
systemctl enable modem_gps.service
systemctl daemon-reload
systemctl status modem_gps

 
