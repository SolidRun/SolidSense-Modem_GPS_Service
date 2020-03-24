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
import time

from QuectelAT_Service import *


def main():

    log=logging.getLogger('Modem_GPS_Service')
    log.addHandler(logging.StreamHandler())
    log.setLevel(logging.DEBUG)
    try:
        modem=QuectelModem('/dev/ttyUSB2',True)
    except Exception as err:
        log.error(str(err))
        return

    log.info("SIM Status:"+modem.SIM_Status())
    if modem.checkSIM() == "NO SIM":
        log.error("No SIM card inserted")
        return

    if modem.SIM_Status() == "SIM PIN":
        modem.setpin('0000')
        time.sleep(2.0)
        modem.checkSIM()
    modem.clearFPLMN()
    modem.allowRoaming()
    modem.logModemStatus()
    if modem.SIM_Ready():
        # start the registration process
        modem.resetCard()
        time.sleep(20.)

        # let's see what is the situation
        nb_attempt=0
        while nb_attempt < 10 :
            res=modem.networkStatus()
            state=modem.regStatus()
            print("Modem registration status:",state)
            if res : break
            nb_attempt += 1
            time.sleep(2.0)

    modem.close()


if __name__ == '__main__':
    main()
