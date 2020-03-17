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
    modem=QuectelModem('/dev/ttyUSB2',True)
    log.info("SIM Status:"+modem.SIM_Status())
    if modem.SIM_Status() == "SIM PIN":
        modem.setpin('0000')
        time.sleep(2.0)
        modem.checkSIM()

    modem.logModemStatus()
    if modem.SIM_Ready():
        # we have a SIM so look how it goaes
        res= modem.networkStatus()
        if res :
            # ok we are attached
            modem.logNetworkStatus()
        else:
            # let's see what is the situation
            state=modem.regStatus()
            print(state)
            if state == "IN PROGRESS" :
                # just wait
                print("Registration in progress => waiting")
                nb_attemp=0
                while nb_attempt < 10 :
                    time.sleep(2.0)
                    res=modem.networkStatus()
                    if res : break
            else:
                print(modem.visibleOperators())
                # try to Register from scratch
                # clear forbidden PLMN and allow roaming
                modem.clearFPLMN()
                modem.allowRoaming()
                modem.selectOperator('AUTO')
                time.sleep(10.0)
                res= modem.networkStatus()
                modem.logNetworkStatus()

    modem.close()


if __name__ == '__main__':
    main()
