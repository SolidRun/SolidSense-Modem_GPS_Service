# -*- coding: UTF-8 -*-
#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Laurent Carré
#
# Created:     28/07/2019
# Copyright:   (c) Laurent Carré Sterwen Technologies 2019
# Licence:     <your licence>
#-------------------------------------------------------------------------------


from QuectelAT_Service import *
from Modem_GPS_Parameters import *

mdm_serv_log=logging.getLogger('Modem_GPS_Service')

class Modem_Service():

    def __init__(self):
        self._open=False
        self._modem=None
        self._device=getparam('modem_ctrl')

    def performInit(self):

        self._modem=QuectelModem(self._device)
        # at that point we shall be OK ,there is a modem attached
        self._open=True
        self._modem.logModemStatus()
        # now check if we need and can send the PIN code
        nb_attempt=0
        while nb_attempt < 3 :
            if self._modem.SIM_Ready() :
                if self._modem.networkStatus():
                    self._modem.logNetworkStatus()
                    break
                else:
                    time.sleep(1.0)
                    nb_attempt= nb_attempt+1
            elif self._modem.SIM_Present() :
                if self._modem.SIM_Status() == "SIM PIN" :
                    #  ok we need a PIN code
                    pin=getparam("PIN")
                    if pin == None :
                        break
                    self._modem.setpin(pin)
                    time.sleep(1.0)
                    nb_attempt= nb_attempt+1
            else :
                mdm_serv_log.info("NO SIM CARD")
                break

        return

        def close(self):
            """
            we need to close the control tty to avoid blocking it
            Modem Manager may need it
            """
            self._modem.close()
            self._open=False
            mdm_serv_log.debug("Closing modem interface")

        def open():
            """
            To just reopen the control interface
            """
            self._modem.open()
            self._open=True
            mdm_serv_log.debug("Closing modem interface")

        def startGPS(self):
            if self._open :
                if not self._modem.gpsStatus():
                    # start the GPS
                    self._modem.startGPS()
                mdm_serv_log.debug("GPS started")



def main():
    pass

if __name__ == '__main__':
    main()
