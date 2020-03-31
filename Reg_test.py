#-------------------------------------------------------------------------------
# Name:        Test Modem
# Purpose:     Perform basic testing of the modem function
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


def init(modem):
    modem.resetCard()
    time.sleep(5.)
    # modem.clearFPLMN()
    # modem.allowRoaming()
    modem.logModemStatus()

def COPS(modem):
    resp=modem.sendATcommand("+COPS?")
    for r in resp:
        print(r)

def CEREG(modem):
    resp=modem.sendATcommand("+CEREG?")
    for r in resp:
        print(r)

def main():

    log=logging.getLogger('Modem_GPS_Service')
    log.addHandler(logging.StreamHandler())
    log.setLevel(logging.DEBUG)
    try:
        modem=QuectelModem('/dev/ttyUSB2',True)
    except Exception as err:
        log.error(str(err))
        return

    init(modem)
    log.info("SIM Status:"+modem.SIM_Status())
    if modem.checkSIM() == "NO SIM":
        log.error("No SIM card inserted")
        return


    if modem.SIM_Ready():
        # we have a SIM so look how it goaes
        COPS(modem)
        res= modem.networkStatus()
        CEREG(modem)
        nb_attempt=0
        while not res :
            # let's see what is the situation
            time.sleep(10.)
            COPS(modem)
            res= modem.networkStatus()
            CEREG(modem)
            state=modem.regStatus()
            print("Modem registration status:",state)
            nb_attempt += 1
            if nb_attempt > 11: break

    modem.close()


if __name__ == '__main__':
    main()
