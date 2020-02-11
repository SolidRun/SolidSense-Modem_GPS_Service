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
    modem=QuectelModem('/dev/ttyUSB3',True)
    modem.logModemStatus()
    if len(sys.argv) > 1:
        if sys.argv[1] == 'FULL' :
            log.info("Resetting paramaters to default")
            modem.sendATcommand("&F0",True)
        log.info("Resetting the card")
        modem.resetCard()

    modem.close()


if __name__ == '__main__':
    main()
