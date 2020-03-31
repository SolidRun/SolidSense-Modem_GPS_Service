#-------------------------------------------------------------------------------
# Name:        ATcmd
# Purpose:     send a single AT command to the modem
#
# Author:      Laurent Carré
#
# Created:     31/03/2020
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
    modem=QuectelModem('/dev/ttyUSB2',False,False)
    # modem.logModemStatus()

    if len(sys.argv) > 1:
        print("sending:",sys.argv[1])
        resp=modem.sendATcommand(sys.argv[1],False)
        for r in resp:
            print(r)

    modem.close()



if __name__ == '__main__':
    main()
