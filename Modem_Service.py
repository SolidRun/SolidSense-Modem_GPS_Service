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

import threading
import os
from QuectelAT_Service import *
from Modem_GPS_Parameters import *

mdm_serv_log=None

class Modem_Service():

    def __init__(self):
        global mdm_serv_log
        mdm_serv_log=logging.getLogger('Modem_GPS_Service')
        self._openFlag=False
        self._modem=None
        self._device=getparam('modem_ctrl')
        self._statusLock= threading.Lock()
        self._error_count=0

    def checkCard(self):
        try:
            os.stat(self._device)
        except FileNotFoundError :
            return False
        return True

    def modemReset(self):
        self._modem.resetCard()
        time.sleep(30.)

    def performInit(self):

        if getparam('log_at') == True:
            log_at=True
        else:
            log_at=False

        self._modem=QuectelModem(self._device,log_at)
        # at that point we shall be OK ,there is a modem attached
        self._openFlag=True
        self._modem.logModemStatus()
        if not self._modem.SIM_Present() :
            # no SIM, no need to continue
            return False
        # now check if we need and can send the PIN code and perform init
        init_done=False
        nb_attempt=0
        send_select=False
        pin_set=False
        while nb_attempt < 3 :
            mdm_serv_log.debug("Modem setup attempt#"+str(nb_attempt))
            if self._modem.SIM_Ready() :
                mdm_serv_log.debug("Modem setup SIM status:"+self._modem.SIM_Status())
                # perform SIM init sequence

                if not init_done :
                    # clearing forbidden PLMN list
                    self._modem.clearFPLMN()
                    roaming=getparam("roaming")
                    if roaming != None and roaming :
                        # print("allowing roaming")
                        self._modem.allowRoaming()
                    self._modem.configureSMS()
                    init_done = True

                # the SIM is ready so look in operatorsDB
                if not self._modem.readOperatorNames(buildFileName('operatorsDB')) :
                    # file or SIM has been change => rebuild and save
                    self._modem.saveOperatorNames(buildFileName('operatorsDB'))
                if self._modem.networkStatus():
                    # self._modem.logNetworkStatus()
                    # modem is attached (registered) so nothing else to do
                    break
                else:
                    # SIM is ready but we have a registration problem
                    if self._modem.regStatus() == "DENIED" or self._modem.regStatus() == "NO REG":
                        # force to look to all network and then wait
                        self._modem.selectOperator('AUTO')
                        # let's stop as we can't do much here
                        break
                    else:
                        time.sleep(2.0)
                        # return True

                    nb_attempt= nb_attempt+1

            elif self._modem.SIM_Present() and not pin_set:
                if self._modem.SIM_Status() == "SIM PIN" :
                    #  ok we need a PIN code
                    pin=getparam("PIN")
                    if pin == None :
                        break
                    mdm_serv_log.debug("Modem setup setting PIN to:"+pin)
                    self._modem.setpin(pin)
                    pin_set=True
                    time.sleep(2.0)
                    self._modem.checkSIM()
                    nb_attempt= nb_attempt+1
            else :
                mdm_serv_log.info("NO SIM CARD")
                break
        #
        #  now check the GPS status
        #
        mdm_serv_log.debug("Checking GPS status")
        gps_stat=self._modem.getGpsStatus()
        mdm_serv_log.debug("GPS "+str(gps_stat))
        '''
        Now we need to start a timer to read the network status regularly
        '''
        if self._modem.SIM_Ready():
            mdm_serv_log.debug("Arming timer for periodic reading")
            self.armTimer()
        return False


    def lockModem(self):
        # lock to avoid mixed transactions
        if self._statusLock.acquire(blocking=True,timeout=120.) :
            return
        # one thread is blocking => better to stop the service
        mdm_serv_log.critical("Modem service thread deadlock => restart")
        os._exit(2)

    def unlockModem(self):
        self._statusLock.release()

    def readStatus(self):
        self.lockModem()
        mdm_serv_log.debug("Reading status begin")
        nb_retry=getparam('nb_retry')
        if nb_retry == None: nb_retry =5
        self.open()
        if self._modem.networkStatus() :
            self._error_count = 0
        else:
            self._error_count += 1
            if self._error_count > nb_retry:
                # here we have 10 times in a row a registration error
                # better to attemp something else
                mdm_serv_log.critical("Modem not registered after "+str(self._error_count - 1)+" attempt => RESET")
                self._modem.resetCard()
                # self._modem.factoryDefault()
                self._modem.closeAtLog()
                time.sleep(30.)
                os._exit(2)  # systemd shall restart the service
        # gps status
        if self._modem.gpsStatus():
            gps=self._modem.getGpsStatus()
            if gps['fix'] :
                logstr="GPS Fixed Time {} Lat {} Long {} Speed {}".format(
                    gps['Time_UTC'],gps['Latitude'],gps['Longitude'],gps['SOG_KMH'])
            else:
                logstr="GPS NOT Fixed"
            mdm_serv_log.info(logstr)
            self.close()
        mdm_serv_log.debug("reading status ends")
        self.unlockModem()

    @staticmethod
    def statusTimer(args):
        #print("Modem status timer lapse")
        mdm=args
        mdm.readStatus()
        mdm.armTimer()

    def armTimer(self) :
        delay=getparam('timer')
        if delay == None : delay=60.
        a=[self]
        self._timer=threading.Timer(delay,Modem_Service.statusTimer,args=a)
        self._timer.start()

    def close(self):
        """
        we need to close the control tty to avoid blocking it
        Modem Manager may need it
        """
        self._modem.close()
        self._openFlag=False
        mdm_serv_log.debug("Closing modem interface")

    def open(self):
        """
        To just reopen the control interface
        """
        self._modem.open()
        self._openFlag=True
        mdm_serv_log.debug("Opening modem interface")

    def startGPS(self):
        if self._openFlag :
            mdm_serv_log.debug("Modem service => starting GPS")
            if not self._modem.gpsStatus():
                # start the GPS
                # print("GPS not started => let's start it")
                self._modem.gpsOn()
                if self._modem.gpsStatus():
                    mdm_serv_log.info("Modem service => GPS started")
                else:
                    mdm_serv_log.error("Modem Service => failed to start the GPS")
        else:
            mdm_serv_log.critical("Modem service => progam GPS ERROR")

    def controlIf(self):
        return self._device

    def executeCommand(self,cmd_line):
        # mdm_serv_log.debug("Modem command:"+cmd_line)
        cmdt=cmd_line.split(',')
        cmd=cmdt[0]
        if not self._openFlag :
            self.open()
        if cmd == 'status' or cmd == 'operator' :
            self.lockModem()
            mdm_serv_log.debug("command status begins")
            self.open()
            showOp=False
            # if self._modem.networkStatus() :
            # operator command must be executed even if the modem is not attached
            if cmd == 'operator':
                if len(cmdt) > 1 :
                    # here we try to set the operator
                    if len(cmdt) > 2 :
                        rat=cmdt[2]
                    else:
                        rat=None
                    if cmdt[1].isdecimal():
                        f='numeric'
                    else:
                        f='long'

                    self._modem.selectOperator(cmdt[1],name_format=f,rat=rat)
                else:
                    showOp=True
            '''
            else:
                if cmd == 'operator':
                    showOp = True # in all case we can show operators
            '''

            # print("#################",showOp)
            resp_dict=self._modem.modemStatus(showOp)
            self.close()
            mdm_serv_log.debug("command status ends")
            self.unlockModem()
            resp_msg="OK"
        elif cmd == "reset":
            self._modem.resetCard()
            time.sleep(10.0)
            resp_msg="RESTART"
            resp_dict=None
        elif cmd == "stop":
            resp_msg="STOP"
            resp_dict=None
        else:
            resp_msg="Unkown command"
            resp_dict=None
        self.close()
        return (resp_msg,resp_dict)

    def sendSMS(self,da,text):
        if self._modem.isRegistered() :
            self.lockModem()
            self.open()
            res=self._modem.sendSMS(da,text)
            self.close()
            self.unlockModem()
            return res

    def checkSMS(self,delete):
        if self._modem.isRegistered() :
            self.lockModem()
            self.open()
            msgs=self._modem.checkAllSMS(delete)
            self.close()
            self.unlockModem()
            return msgs
        else:
            return None

def main():
    pass

if __name__ == '__main__':
    main()
