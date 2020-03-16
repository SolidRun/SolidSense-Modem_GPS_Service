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
        # clear forbidden PLMN and allow roaming
        modem.clearFPLMN()
        modem.allowRoaming()
        modem.selectOperator('AUTO')
        res= modem.networkStatus()
        modem.logNetworkStatus()
        if not res :
            print(modem.visibleOperators())
        #else:
           # modem.selectOperator('CURRENT',rat="LTE")
    modem.close()


if __name__ == '__main__':
    main()
