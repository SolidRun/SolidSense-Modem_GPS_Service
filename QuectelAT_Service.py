# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        Quectel modem manager
# Purpose:
#
# Author:      Laurent Carré
#
# Created:     26/06/2019
# Copyright:   (c) Laurent Carré Sterwen Technologies 2019
# Licence:     Eclipse Public License 1.0
#-------------------------------------------------------------------------------

import serial
import sys,os,stat
import time
import json
import datetime
import logging
import subprocess


modem_log=None
test_counter=0


class ModemException(Exception) :
    pass


def findUsbModem(mfg):
    '''
    Look on the USB system and detect the modem from the manufacturer
    '''
    local_log= logging.getLogger('Modem_GPS_Service')
    r=subprocess.run('lsusb',capture_output=True)
    lines=r.stdout.decode('utf-8').split('\n')
    found_modem=False
    for line in lines :
        if len(line) > 0 :
            # print(line)
            if line.find(mfg)  > 0 :
                t=line.split(' ')
                bus=int(t[1])
                dev=int(t[3].rstrip(':'))
                ids=t[5].split(':')
                found_modem=True
                break
    if found_modem :
        out={}
        # check the device path
        r=subprocess.run("ls /sys/bus/usb/drivers/option/ | head -n1 | cut -f1 -d':'",capture_output=True,shell=True)
        dev_path=r.stdout.decode('utf-8').rstrip('\n')
        local_log.info("Found "+mfg+" modem on USB bus "+str(bus)+" device "+str(dev)+' Device path:'+dev_path)
        out['bus']=bus
        out['dev'] = dev
        out['mfgid']=ids[0]
        out['modelid'] = ids[1]
        out['dev_path'] = dev_path
        # local_log.debug("Modem found:"+str(out))
        return out
    else:
        local_log.error('No '+mfg+' modem found')
        return None


class QuectelModem():

    @staticmethod
    def checkModemPresence():
        return findUsbModem('Quectel')

    def __init__(self,ifName,log=False,init=True):
        global modem_log
        modem_log=logging.getLogger('Modem_GPS_Service')
        self._ifname = ifName
        self.open()
        self._logAT=log
        if self._logAT :
            self._logfp=open("/data/solidsense/modem_gps/atcmd.log","a")
            header="*** New session %s ****\n"% datetime.datetime.now().isoformat(' ')
            self._logfp.write(header)

        self._isRegistered= False
        self._networkReg="UNKNOWN"
        if init :
            self.initialize()
        self._operatorNames=None # dictionary PLMN/Operator name
        return

    def open(self):
        try:
            self._tty=serial.Serial(self._ifname,timeout=10.0)
        except serial.SerialException as err:
            # print "Opening:",ifName," :",err
            raise ModemException("Open modem:"+self._ifname+" error:"+str(err))
        return

    def close(self):
        self._tty.close()
        if self._logAT :
            self._logfp.flush()

    def closeAtLog(self):
        if self._logAT :
            header= "*** End of session %s ****\n"% datetime.datetime.now().isoformat(' ')
            self._logfp.write(header)
            self._logfp.flush()
            self._logfp.close()
            self._logAT=False

    def logATCommand(self,cmd):
        if self._logAT :
            buf= datetime.datetime.now().strftime("%H:%M:%S.%f >")
            buf += cmd
            self._logfp.write(buf)
    #
    # send AT command and return the responses
    #
    def writeATBuffer(self,buf):
        # print buf
        if self._logAT :
            self.logATCommand(buf)

        try:
            self._tty.write(buf.encode())
            self._tty.flush()
        except serial.serialutil.SerialException as err :
            modem_log.error ("Send AT command Write error "+ str(err)+" command:"+buf)
            if self._logAT:
                self._logfp.write(err+"\n")
            raise ModemException(err)

    def readATResponse(self,param,raiseException):
        readResp=True
        nbResp=0
        respList=list()
        while readResp:
            # reading one response
            # self._tty.timeout=10.0
            try:
                resp=self._tty.read_until().decode()
            except serial.serialutil.SerialException as err :
                modem_log.error ("Read at Command Error:"+str(err))
                if self._logAT :
                    self._logfp.write(err+"\n")
                readResp=False
                break
            if self._logAT:
                self._logfp.write(resp)
            cleanResp=resp.strip('\n\r')
            #analysis of the response
            if cleanResp == "OK" :
                readResp=False
            elif cleanResp == "ERROR" :
                readResp=False
                if raiseException :
                    raise ModemException(param+" ERROR")
            elif cleanResp == "NO CARRIER":
                readResp=False
                if raiseException :
                    raise ModemException(param+" NO CARRIER")
            elif cleanResp.startswith("+CME") or cleanResp.startswith("+CMS"):
                readResp=False
                modem_log.debug(cleanResp)
                respList.append(cleanResp)
                if raiseException :
                    raise ModemException(cleanResp)
            else :
                if len(cleanResp) > 0 :
                     respList.append(cleanResp)
                     nbResp=nbResp+1
        # print "Number of responses:",nbResp
        return respList

    def sendATcommand(self,param=None,raiseException=False):
        buf="AT"
        if param != None :
            buf=buf+param
        buf= buf +'\r'
        self.writeATBuffer(buf)
        return self.readATResponse(param,raiseException)

    #
    # perform initialisation of the modem parameters
    #
    def initialize(self):
        self.sendATcommand("E0") # remove echo
        r=self.sendATcommand("I")
        if r[0] != "Quectel" :
            # print "Wrong manufacturer:",r
            raise ModemException("Wrong manufacturer:"+str(r))
            return
        self._model=r[1]
        self._rev=r[2]
        r=self.sendATcommand("+GSN") # return IMEI
        self._IMEI=r[0]
        #check IMEI-SVN mode
        '''
        removing SVN management as part of issue #450
        r=self.sendATcommand("+EGMR=0,9")
        # print r
        svn=self.splitResponse("+EGMR",r[0])
        self._svn=svn[0]
        '''
        self.checkSIM()


    def checkSIM(self):
        # check if SIM is present
        r=self.sendATcommand("+QSIMSTAT?")
        sim_status_read=False
        for resp in r:
            cmd=self.checkResponse(resp)
            if cmd== "+QSIMSTAT" :
                sim_flags=self.splitResponse("+QSIMSTAT",resp)
            elif cmd == "+CPIN" :
                sim_lock= self.splitResponse("+CPIN",resp)
                sim_status_read = True

        # print("SIM FLAGS=",sim_flags)
        if sim_flags[1] == 1 :
            # there is a SIM inserted
            self._SIM=True
            if not sim_status_read :
                r=self.sendATcommand("+CPIN?")
                sim_lock=self.splitResponse("+CPIN",r[0])
            # print("SIM lock=",sim_lock[0])
            self._SIM_STATUS=sim_lock[0]
            if sim_lock[0] == "READY":
                r=self.sendATcommand("+CIMI")
                self._IMSI=r[0]
                r=self.sendATcommand("+QCCID")
                r=self.splitResponse("+QCCID",r[0])
                self._ICCID=r[0]
                # print("ICCID:",self._ICCID,"Type:",type(self._ICCID))
                # allow full notifications on registration change
                self.sendATcommand("+CREG=2")
        else:
            self._SIM=False

    def model(self):
        return self._model

    def manufacturer(self):
        return "Quectel"

    def SIM_Ready(self):
        return self._SIM and self._SIM_STATUS == "READY"

    def SIM_Present(self):
        return self._SIM

    def SIM_Status(self):
        if self._SIM :
            return self._SIM_STATUS
        else:
            return "NO SIM"

    def IMEI(self):
        return self._IMEI
    def IMSI(self):
        if self._SIM and self._SIM_STATUS=="READY":
            return self._IMSI
        else:
            return None
    def ICCID(self):
        if self._SIM and self._SIM_STATUS=="READY":
            return self._ICCID
        else:
            return None

    def setpin(self,pin) :
        cmd="+CPIN="+pin
        try:
            self.sendATcommand(cmd)
        except ModemException as err:
            modem_log.error("Modem set PIN :"+str(err))

    #
    # allow roaming
    #
    def allowRoaming(self):
        r=self.sendATcommand("+QCFG=\"roamservice\"")
        modem_log.debug("Modem roaming configuration:"+r[0])
        rs=self.splitResponse("+QCFG",r[0])
        # print("roaming flag:",rs[1])
        if rs[1] != 2 :
            modem_log.debug("Allowing roaming while not allowed")
            r=self.sendATcommand("+QCFG=\"roamservice\",2,1")

    def clearFPLMN(self):
        """
        clearing forbidden PLMN list
        """
        # print("Clearing FPLMN")
        try:
            r=self.sendATcommand("+CRSM=214,28539,0,0,12,\"FFFFFFFFFFFFFFFFFFFFFFFF\"",True)
        except ModemException as err :
            modem_log.error("Error during Clearing FPLMN="+str(err))

    #
    #   split a complex response in several fields
    #
    def splitResponse(self,cmd,resp,raiseException=True) :
        st=resp.find(cmd)
        if st == -1 :
            modem_log.error("Modem sent unexpected response:"+cmd+" response:"+resp)
            if raiseException :
                raise ModemException ("Wrong response:"+cmd+" : "+resp)
            return None
        st=len(cmd)+2 # one for colon + one for space
        toSplit=resp[st:]
        param=list()
        for s in toSplit.split(',')  :
            # check if we have double quote
            if len(s) == 0 :
                continue
            # print "|",s,"|"
            if s[0] == '"' :
                s=s[1:len(s)-1]
            if s.isdigit() :
                param.append(int(s))
            else:
                param.append(s)
        return param


    def checkResponse(self,resp) :
        """
        analyse response with unknown command inside
        """
        try:
            cmd=resp.index(':')
        except ValueError :
            modem_log.error("Unable to decode response:"+resp)
            return " "
        return resp[:cmd]

    def checkAndSplitResponse(self,cmd,resp):
        '''
        check if the expected response is returned
        and then split it for processing
        '''
        for r in resp:
            param = self.splitResponse(cmd,r,False)
            if param != None :
                return param
            else:
                modem_log.debug("AT cmd="+cmd+"response:"+str(r))
        # nothing found
        modem_log.error("No AT response for:"+cmd)
        return None

    def networkStatus(self,log=True):

        if not self.SIM_Ready() :
            return False
        # self.sendATcommand("+CREG=2")
        # self._networkReg = None
        '''
        global test_counter
        test_counter += 1
        if test_counter > 2 :
            modem_log.info("Test = error simutation")
            return False
        '''
        resp=self.sendATcommand("+CREG?")
        # warning some spontaneous messages can come
        vresp=self.checkAndSplitResponse("+CREG",resp)
        if vresp == None :
            modem_log.error("No registration status returned (+CREG)")
            return False
        return self.decodeRegistration(vresp,log)

    def regStatus(self):
        return self._networkReg

    def decodeRegistration(self,param,log):
        '''
        Decode the registration message
        Read all network attachment characteristics
        '''

        # param=self.splitResponse("+CREG",vresp)
        # modem_log.info("Network registration status:"+str(param[1]))
        # in some case param is only a single value
        if len(param) < 2 :
            return False

        if param[1] == 1 :
            if log : modem_log.info ("registered on home operator")
            self._networkReg="HOME"
        elif param[1] == 5 :
            if log : modem_log.info ("registered on roaming" )
            self._networkReg="ROAMING"
        else:
            '''
            Correction of issue 534
            If the modem is not actively looking for a network
            Then we need to restart the sequence
            '''
            # modem_log.info ("not registered")
            if param[1] == 3 :
                modem_log.info ("registration DENIED")
                self._networkReg="DENIED"
            elif param[1] == 2 :
                modem_log.info("Registration in progress. looking for a network...")
                self._networkReg="IN PROGRESS"
            else:
                modem_log.error("No registration in progress...")
                self._networkReg="NO REG"
            return False

        # print ("n:",param[0])
        # get lac and ci
        if param[0] == 2 :
            try:
                if type(param[2]) == int :
                    self._lac = param[2]
                else:
                    self._lac=int(param[2],16)
                if type(param[3]) == int:
                    self._ci = param[3]
                else:
                    self._ci=int(param[3],16)
            except (ValueError,TypeError) :
                modem_log.error("Error decoding LAC or CI")
                print("LAC:",param[2],"CI:",param[3])
                print(type(param[2]),type(param[3]))
                self._lac=0
                self._ci=0
        else:
            self._lac=0
            self._ci=0
        #
        #  get operator name
        #

        resp=self.sendATcommand("+QSPN")
        param=self.checkAndSplitResponse("+QSPN",resp)
        if param != None:
            self._networkName=param[0]
            self._regPLMN=param[4]
        else:
            self._networkName="Unknown"
            self._regPLMN=0

        self._isRegistered = True
        #
        # Get quality indicators
        #
        # print("Decoding network info")
        resp=self.sendATcommand("+QNWINFO")
        param=self.checkAndSplitResponse("+QNWINFO",resp)
        if param != None :
            self.decodeNetworkInfo(param)
        else:
            modem_log.error("Error on network info")
            return True

        if log :
            logstr="Registered on {0}/{1} PLMID {2} LAC {3} CI {7} RAT {4} BAND {5} RSSI {6}".format(self._networkName,self._networkReg,self._regPLMN,self._lac,self._rat,self._band,self._rssi,self._ci)
            modem_log.info(logstr)
        return True

    def decodeNetworkInfo(self,param):

        #param=self.splitResponse("+QNWINFO",resp)
        self._rat=param[0]
        if len(param) >= 3 :
            self._band=param[2]
        else:
            self._band="unknown"

        resp=self.sendATcommand("+CSQ")
        param=self.checkAndSplitResponse("+CSQ",resp)
        if param == None :
            self._rssi=0
            return
        #print("Quality indicator:",param)
        if param[0] <= 31 :
            self._rssi= -113 +(param[0]*2)
        elif param[0] >= 100 and param[0] <= 191 :
            self._rssi= -116 + (param[0] - 100 )
        else:
            self._rssi= 99

    """
    def networkInfo(self):
        '''
        Check the network information RAT/PLMNID/BAND
        if registration has changed then go for full registration decoding
        '''


        if not self.SIM_Ready() :
            # pointless to continue
            modem_log.info("Network Info => No SIM")
            return False
        if not self._isRegistered :
            # no registration, so no need to get further action
            modem_log.info("Network info => not registered: "+self._networkReg)
            return False

        resp=self.sendATcommand("+QNWINFO")
        regresp=None
        inforesp=None
        for r in resp:

            if self.checkResponse(r) == "+QNWINFO"  :
                inforesp=  r
            elif self.checkResponse(r) == "+CREG":
                regresp=r

        if regresp != None :
            return self.decodeRegistration(regresp,log=False)
        else:
            self.networkStatus(False)
        if inforesp == None :
            modem_log.error("Error reading network info")
            return False
        self.decodeNetworkInfo(inforesp)
        logstr="Network {4} {0} LAC:{2} CI:{3} RSSI:{1}".format(self._band,self._rssi,self._lac,self._ci,self._regPLMN)
        modem_log.info(logstr)


        return True
    """

    def readOperatorNames(self,fileName):
        if self._operatorNames is not None :
            # already in memory
            return True
        if os.path.exists(fileName) :
            # print ("reading",fileName)
            try:
                fp=open(fileName,"r")
            except IOError as err:
                modem_log.info ("Reading operators database:"+fileName+" :"+str(err))
                return False
            try:
                in_str= json.load(fp)
            except json.JSONDecodeError :
                # wrong format
                modem_log.error("Reading operators database:"+fileName+" Format error")
                fp.close()
                return False
            if in_str['IMSI'] != self._IMSI :
                # SIM has been changed - information is void
                modem_log.info("SIM CARD Changed")
                fp.close()
                return False

            self._operatorNames=in_str['operators']
            modem_log.info ("Succefully read operators DB with:"+str(len(self._operatorNames))+" entries")
            fp.close()
            return True
        else:
            return False

    def saveOperatorNames(self, fileName):
        # print("saving operators DB")
        if not self.SIM_Ready() :
            return
        try:
            fp=open(fileName,"w")
        except OSError as err:
            modem_log.error ("Writing operators database:"+fileName+" :"+str(err))
            return
        # now retrieve all network names
        resp=self.sendATcommand("+COPN")
        self._operatorNames={}
        nbOper=0
        out={}
        out['IMSI']=self._IMSI
        for r in resp:
            oper=self.splitResponse("+COPN",r)
            # print oper[0],",",oper[1]
            plmnid=oper[0]
            self._operatorNames[plmnid]=oper[1]
            nbOper=nbOper+1
        out['operators'] = self._operatorNames
        # now save in file
        json.dump(out,fp)
        modem_log.info ("Saved "+str(nbOper)+" names in:"+fileName)
        fp.close()

    #
    #  display visible operators
    #
    def visibleOperators(self):
        access = { 0 : 'Unknown', 1 : 'Available', 2:'Current', 3:'Forbidden'}
        rat = {0:'GSM',2:'UTRAN',3:'GSM/GPRS',4:'3G HSDPA',5:'3G HSUPA',
          6:'3G HSDPA/HSUPA',7:'LTE',100:'CDMA'}
        # print ("Looking for operators....." )
        modem_log.info("Start looking for visible networks...")
        resp=self.sendATcommand("+COPS=?")
        modem_log.info("End of networks search")
        if len(resp) == 0 :
            result=''
            return
        oper=resp[0].split('(')
        result=''
        # print ("Operators visible by the modem")
        for o in oper[1:] :
            # print o
            fields=o.split(',')
            if len(fields) < 5 :
                # print( "Strange operator:",o )
                continue
            a=int(fields[0])
            o=fields[1][1:len(fields[1])-1]
            p=int(fields[3][1:len(fields[3])-1] )
            ip=fields[4].find(')')
            #print fields[4],ip
            r=int(fields[4][:ip])
            try:
                # print (o,":",access[a],"PLMN:",self.decodePLMN(p)," AT:",rat[r])
                res = "%s: %s - PLMN %d/%s - RAT: %s" % (o,access[a],p,str(self.decodePLMN(p)),rat[r])
                modem_log.info(res)
                result += res + '\n'
            except KeyError :
                continue
        return result

    def selectOperator(self,operator,name_format='long',rat=None):
        '''
        select an operator => automatic if failed
        '''
        rat_index={ "GSM":0,"UTRAN":2,"LTE":7}
        modem_log.info("Selecting the operator:"+str(operator)+" with RAT:"+str(rat))
        if operator == "CURRENT" :
            operator = self._networkName
            name_format='long'

        if operator == 'AUTO':
            cmd = "+COPS=0"
        else:
            if name_format == 'long':
                cmd="+COPS=1,0,%s" % operator
            else:
                cmd="+COPS=1,2,%s" % str(operator)
            if rat is not None :
                rat_idx=rat_index.get(rat,None)
            else:
                rat_idx=None
            if rat_idx is not None:
                cmd += ","+str(rat_idx)
        try:
            modem_log.debug("Select operator CMD: "+cmd)
            resp=self.sendATcommand(cmd,raiseException=True)
        except ModemException as err:
            modem_log.error("Failed to set operator:"+str(operator))
            return
        self.networkStatus()

    def decodePLMN(self,plmnid) :

        if type(plmnid) != str :
            plmn = "%d" % plmnid
        else:
            plmn=plmnid
        if self._operatorNames is not None :
            # print "PLMN number:",plmnid
            try:
                network=self._operatorNames[plmn]
            except KeyError:
                modem_log.debug ("No PLMID:"+plmn)
                network=str(plmn)
        else:
            network=str(plmn)
        return network

    def isRegistered(self):
        return self._isRegistered

    def logNetworkStatus(self):
        if not self._isRegistered :
            modem_log.info ("Not registered")
        else:
            modem_log.info (self._networkReg+":"+self._networkName+" PLMN:"+\
                  self.decodePLMN(self._regPLMN)+" Radio:"+self._rat+" Band:"+self._band+" RSSI:"+str(self._rssi)+"dBm" )

    def logModemStatus(self,output=sys.stdout):
        modem_log.info ("Quectel modem "+self._model+self._rev)
        # removing SVN display
        modem_log.info ("IMEI: %s -%d digits (incl CRC)" % (self._IMEI,len(self._IMEI)) )
        if self._SIM :
            modem_log.info ("SIM STATUS:"+self._SIM_STATUS)
            if self._SIM_STATUS== "READY" : modem_log.info ("SIM IMSI:"+self._IMSI+" ICC-ID:"+str(self.ICCID()))
        else :
            modem_log.info ("NO SIM Inserted"  )

    def modemStatus(self,showOperators=False):
        out = {'model': self._model + " " + self._rev, 'IMEI': self.IMEI()}
        if self.gpsStatus() :
            out['gps_on']=True
        else:
            out['gps_on'] = False
        out['SIM_status']= self.SIM_Status()
        if self.SIM_Present() :
            out['IMSI'] = self.IMSI()
            out['ICCID'] = str(self.ICCID())
            if self._isRegistered :
                out['registered'] = True
                out['network_reg']= self._networkReg
                out['PLMNID']=self._regPLMN
                out['network_name'] = self._networkName
                out['network']=self.decodePLMN(self._regPLMN)
                out['lac'] = self._lac
                out['ci'] = self._ci
                out['rat']  = self._rat
                out['band'] = self._band
                out['rssi'] = self._rssi
                if showOperators :
                   out['operators']  =self.visibleOperators()
            else:
                out['registered']  = False
                if showOperators :
                    out['operators'] = self.visibleOperators()

        return out
    #
    # perform a modem reset
    #

    def resetCard(self):
        modem_log.info ("TURNING RADIO OFF AND ON")
        modem_log.debug("Going to flight mode")
        self.sendATcommand("+CFUN=0",raiseException=True)
        time.sleep(5.0) # 5 sec recommended by Quectel
        modem_log.debug("Restoring normal mode")
        self.sendATcommand("+CFUN=1",raiseException=True)
        modem_log.info ("Allow 20-30 sec for the modem to restart")
        # time.sleep(20)

    def factoryDefault(self):
        modem_log.info("RESTORING FACTORY DEFAULT")
        self.sendATcommand("+QPRTPARA=3")
        time.sleep(1.0)
        modem_log.info("RESETTING THE MODEM")
        self.sendATcommand("+CFUN=1,1")
        self.close()
        modem_log.info ("Allow 20-30 sec for the modem to restart")
    #
    # turn GPS on with output on ttyUSB1 as NMEA sentence
    #
    def gpsOn(self):

        resp=self.sendATcommand("+QGPSCFG=\"outport\",\"usbnmea\"",True)
        resp=self.sendATcommand("+QGPSCFG=\"autogps\",1",True)
        resp=self.sendATcommand("+QGPS=1",True)

    def gpsOff(self):
        resp=self.sendATcommand("+QGPSEND",True)
        resp=self.sendATcommand("+QGPSCFG=\"autogps\",0",True)

    def getGpsStatus(self):
        status={}
        if not self.gpsStatus() :
            status['state'] ='off'
            return  status
        #
        # now the GPS is on let's see what have
        #
        status['state']='on'
        # modem_log.debug("GPS is ON")
        #
        # check NMEA port
        #
        # modem_log.debug("Reading NMEA port parameters")
        resp=self.sendATcommand("+QGPSCFG=\"outport\"")
        param=self.checkAndSplitResponse("+QGPSCFG",resp)
        status["NMEA_port1"]=param[0]
        status['NMEA_port2']=param[1]
        # read values
        # modem_log.debug("Reading GPS via AT")
        resp=self.sendATcommand("+QGPSLOC=0",False)
        #print("GPS RESP=",resp)
        # check that we are fixed
        cmd=self.checkResponse(resp[0])
        if cmd.startswith('+CME') :
            err=int(self.splitResponse("+CME ERROR",resp[0])[0] )
            # print("ERROR=",err)
            if err == 516 :
                status ['fix']=False
            else:
                status ['fix'] = err
            return status
        # now we shall have a valid GPS signal

        param=self.checkAndSplitResponse("+QGPSLOC",resp)
        if param is None:
            status['fix'] = False
        else:
            status['fix'] = True
            status["Time_UTC"]=param[0]
            status["Latitude"]=param[1]
            status['Longitude']=param[2]
            status['hdop']=param[3]
            status['Altitude']=param[4]
            status['date']=param[9]
            status["nbsat" ]=param[10]
            status["SOG_KMH"]=param[8]
        return status

    def gpsStatus(self):
        resp=self.sendATcommand("+QGPS?")
        param=self.checkAndSplitResponse("+QGPS", resp)
        if param is None:
            return False
        if param[0] == 0:
            return False
        else:
            return True

    def gpsPort(self):
        resp=self.sendATcommand("+QGPSCFG=\"outport\"")
        param=self.checkAndSplitResponse("+QGPSCFG",resp)
        return param[1]

    '''

    SMS related methods

    '''

    def configureSMS(self):
        # store all messages in the module
        self.sendATcommand('+CPMS="ME","ME","ME"')
        self.sendATcommand("+CMGF=1")
        self.sendATcommand('+CSCS="GSM"')

    def sendSMS(self,da,text):
        buf='AT+CMGS='+'\"'+da+'\"\r'
        # print(buf)
        self.writeATBuffer(buf)
        # read the first response
        resp=self._tty.read_until()
        prompt=self._tty.read(1)
        # print("Prompt received:",prompt[0])
        if prompt[0] != 62 :
            resp[0]=prompt[0]
            buf=self._tty.read_until()
            resp=(resp.append(buf)).decode()
            resp=resp.strip('\r\n')
            modem_log.error("Error sending SMS:"+resp)
            return "SEND ERROR"
        else:
            buf2= text+'\x1a'
            # print(buf2)
            self.writeATBuffer(buf2)
            resp=self.readATResponse("+CMGS",False)
            # print(resp)
            if resp != None :

                result=self.checkResponse(resp[1])
                if result.startswith("+CMS") :
                    error=self.splitResponse("+CMS ERROR",resp[1])
                    modem_log.error("Error sending SMS:"+str(error[0])+" to:"+da)
                    return resp[1]
                else:
                    modem_log.info("SMS sent to:"+da)
                    return "OK"

    def readSMS(self,stat):
        cmd='+CMGL="%s"' % stat
        resp=self.sendATcommand(cmd)
        messages=[]
        for r in resp :
            if r.startswith('+CMGL') :
                msg={}
                msg_part=self.splitResponse('+CMGL',r)
                msg['index']=msg_part[0]
                msg['status']=msg_part[1]
                msg['origin']=msg_part[2]
                msg['sms_time']=msg_part[4]
                # modem_log.debug("Message received from:"+msg_part[2])
            else:
                r=r.strip('\r\n')
                msg['text']=r
                # modem_log.debug("Content:"+r)
                messages.append(msg)
        modem_log.info("Number of SMS collected:"+str(len(messages)))
        return messages

    def checkReceivedSMS(self):
        # read messages
        modem_log.debug("Reading unread SMS from modem")
        return self.readSMS('REC UNREAD')

    def checkAllSMS(self,delete=False):
        modem_log.debug("Reading all SMS from modem")
        msgs=self.readSMS('ALL')
        if delete :
            self.sendATcommand('+CMGD=1,1')
        return msgs





