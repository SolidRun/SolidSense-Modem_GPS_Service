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

def checkSMS(modem):
    resp=modem.sendATcommand("+CSMS?")
    s=modem.splitResponse("+CSMS",resp[0])
    print("SMS service type",s[0],"MO:",s[1],"MT:",s[2],"BM:",s[3])
    resp=modem.sendATcommand("+CSCA?")
    s=modem.splitResponse("+CSCA",resp[0])
    print("SMS Service center:",s[0])


def init(modem):
    modem.resetCard()
    time.sleep(20.)
    modem.clearFPLMN()
    modem.allowRoaming()
    modem.logModemStatus()

def rescan(modem):
    print("Resetting network scan mode")
    modem.sendATcommand('+QCFG=”nwscanmode”,0,1')
    modem.selectOperator('AUTO')

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

    option="None"
    if len(sys.argv) > 1 :
        option=sys.argv[1]

    if modem.SIM_Status() == "SIM PIN":
        modem.setpin('0000')
        time.sleep(2.0)
        modem.checkSIM()

    modem.logModemStatus()

    if option == "init" :
        init(modem)
    elif option == "cmd" :
        if len(sys.argv) >2 :
            print("sending:",sys.argv[2])
            resp=modem.sendATcommand(sys.argv[2],True)
            for r in resp:
                print(r)
        else:
            print("Missing command argument")
    elif option == "scan" :
        if modem.SIM_Ready():
            rescan(modem)
    elif option == 'sms' :
        checkSMS(modem)
    else:
        modem.allowRoaming()


    if modem.SIM_Ready():
        # we have a SIM so look how it goaes

        res= modem.networkStatus()

        if not res :
            # let's see what is the situation
            state=modem.regStatus()
            print("Modem registration status:",state)
            if state == "IN PROGRESS" :
                # just wait
                print("Registration in progress => waiting")
                nb_attempt=0
                while nb_attempt < 10 :
                    time.sleep(2.0)
                    res=modem.networkStatus()
                    if res : break
                    nb_attempt += 1
            if not res and option == 'list':
                print(modem.visibleOperators())
                # try to Register from scratch
                # clear forbidden PLMN and allow roaming

    modem.close()


if __name__ == '__main__':
    main()
