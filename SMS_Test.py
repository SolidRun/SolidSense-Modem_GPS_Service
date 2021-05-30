#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Laurent Carré
#
# Created:     11/02/2020
# Copyright:   (c) Laurent Carré Sterwen Technologies 2020
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import logging
import sys

from QuectelAT_Service import *

def main():

    log=logging.getLogger('Modem_GPS_Service')
    log.addHandler(logging.StreamHandler())
    log.setLevel(logging.DEBUG)
    modem=QuectelModem('/dev/ttyUSB2',True)
    modem.logModemStatus()
    modem.configureSMS()
    if len(sys.argv) > 2:

        da=sys.argv[1]
        text=sys.argv[2]
        modem.sendSMS(da,text)
    else:
        print("Read SMS")
        msgs=modem.checkAllSMS(True)
        for m in msgs:
            print("Message #",m['index'],"from:",m['origin'],"at:",m['sms_time']," :",m['text'])


    modem.close()


if __name__ == '__main__':
    main()
