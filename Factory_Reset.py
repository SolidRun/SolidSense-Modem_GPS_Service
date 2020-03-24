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

    if len(sys.argv) > 1:
        if sys.argv[1] == 'FULL' :
            log.info("Resetting paramaters to default")
            modem.factoryDefault()
    else:
        log.info("Performing a soft reset")
        modem.resetCard()
    modem.close()
    log.info("Perform a modem test after 30 sec: modem_status -t")


if __name__ == '__main__':
    main()
