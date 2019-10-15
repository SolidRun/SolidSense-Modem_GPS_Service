# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        Quectel modem manager
# Purpose:
#
# Author:      Laurent Carré
#
# Created:     26/06/2019
# Copyright:   (c) Laurent Carré Sterwen Technologies 2019
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import serial
import sys,os,stat
import time
import json
import datetime
import logging


modem_log=logging.getLogger('Modem_GPS_Service')


class ModemException(Exception) :
    pass

class QuectelModem():


    def __init__(self,ifName,log=False):
        self._ifname = ifName
        self.open()
        self._logAT=log
        if self._logAT :
            self._logfp=open("asmm-atcmd.log","a")
            header="*** New session %s ****\n"% datetime.datetime.now().isoformat(' ')
            self._logfp.write(header)

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
            self._logfp.close()

    #
    # send AT command and return the responses
    #
    def sendATcommand(self,param=None,raiseException=False):
        buf="AT"
        if param != None :
            buf=buf+param
        buf= buf +'\r'
        # print buf
        if self._logAT :
            self._logfp.write(buf)

        try:
            self._tty.write(buf.encode())
            self._tty.flush()
        except serial.serialutil.SerialException as err :
            modem_log.error ("Send AT command Write error"+ str(err))
            if self._logAT:
                self._logfp.write(err+"\n")
            raise ModemException(err)

        readResp=True
        nbResp=0
        respList=list()
        while readResp:
            # reading one response
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
            elif cleanResp.startswith("+CME") :
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
        r=self.sendATcommand("+EGMR=0,9")
        # print r
        svn=self.splitResponse("+EGMR",r[0])
        self._svn=svn[0]
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
        else:
            self._SIM=False

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
        #  print("roaming flag:",rs[1])
        if rs[1] != 2 :
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
    def splitResponse(self,cmd,resp) :
        st=resp.find(cmd)
        if st == -1 :
            raise ModemException ("Wrong response:"+cmd+" : "+resp)
            return
        st=len(cmd)+2 # one for colon + one for space
        toSplit=resp[st:]
        #print toSplit
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
        cmd=resp.index(':')
        return resp[:cmd]


    def networkStatus(self):

        if not self.SIM_Ready() :
            return False
        resp=self.sendATcommand("+CREG?")
        # warning some spontaneous messages can come
        for r in resp:
            if self.checkResponse(r) == '+CREG' :
                vresp=r
        param=self.splitResponse("+CREG",vresp)
        if param[1] == 1 :
            modem_log.info ("registered on home operator")
            self._networkReg="HOME"
        elif param[1] == 5 :
            modem_log.info ("registered on roaming" )
            self._networkReg="ROAMING"
        else:
            modem_log.info ("not registered")
            if param[1] == 3 :
                modem_log.info ("registration DENIED")
            self._networkReg=None
            return False
        # print ("n:",param[0])
        #
        #  get operator name
        #

        resp=self.sendATcommand("+QSPN")
        param=self.splitResponse("+QSPN",resp[0])
        self._networkName=param[0]
        self._regPLMN=param[4]
        #
        # Get quality indicators
        #
        resp=self.sendATcommand("+QNWINFO")
        param=self.splitResponse("+QNWINFO",resp[0])
        self._rat=param[0]
        if len(param) >= 3 :
            self._band=param[2]
        else:
            self._band="unknown"
        resp=self.sendATcommand("+CSQ")
        param=self.splitResponse("+CSQ",resp[0])
        #print("Quality indicator:",param)
        if param[0] <= 30 :
            self._rssi= -113 +(param[0]*2)
        else:
            self._rssi= 99

        return True

    def readOperatorNames(self,fileName):
        if os.path.exists(fileName) :
            # print ("reading",fileName)
            try:
                fp=open(fileName,"r")
            except IOError as err:
                modem_log.info ("Reading operators database:"+fileName+" :"+str(err))
                return
            in_str= json.load(fp)
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


    def saveOperatorNames(self,fileName)  :
        print("saving operators DB")
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
        modem_log.info ("Saved"+str(nbOper)+" names in:"+fileName)
        fp.close()

    #
    #  display visible operators
    #
    def visibleOperators(self):
        access = { 0 : 'Unknown', 1 : 'Available', 2:'Current', 3:'Forbidden'}
        rat = {0:'GSM',2:'UTRAN',3:'GSM/GPRS',4:'3G HSDPA',5:'3G HSUPA',
          6:'3G HSDPA/HSUPA',7:'LTE',100:'CDMA'}
        # print ("Looking for operators....." )
        resp=self.sendATcommand("+COPS=?")
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
                res = "%s: %s - PLMN: %s - RAT: %s" % (o,access[a],str(self.decodePLMN(p)),rat[r])
                modem_log.info(res)
                result += res + '\n'
            except KeyError :
                continue
        return result

    def decodePLMN(self,plmnid) :

        if type(plmnid) != str :
            plmn = "%d" % plmnid
        else:
            plmn=plmnid
        if self._operatorNames != None :
            # print "PLMN number:",plmnid
            try:
                network=self._operatorNames[plmn]
            except KeyError:
                modem_log.debug ("No PLMID:"+plmn)
                network=str(plmn)
        else:
            network=str(plmn)
        return network



    def logNetworkStatus(self):
        if self._networkReg == None :
            modem_log.info ("Not registered")
        else:
            modem_log.info (self._networkReg+":"+self._networkName+" PLMN:"+\
                  self.decodePLMN(self._regPLMN)+" Radio:"+self._rat+" Band:"+self._band+" RSSI:"+str(self._rssi)+"dBm" )

    def logModemStatus(self,output=sys.stdout):
        modem_log.info ("Quectel modem "+self._model+self._rev)

        modem_log.info ("IMEI: %s -%d digits (incl CRC) SVN %02d" % (self._IMEI,len(self._IMEI),self._svn) )
        if self._SIM :
            modem_log.info ("SIM STATUS:"+self._SIM_STATUS)
            if self._SIM_STATUS== "READY" : modem_log.info ("SIM:"+self._IMSI)
        else :
            modem_log.info ("NO SIM Inserted"  )

    def modemStatus(self):
        out={}
        out['model']= self._model+" "+self._rev
        out['IMEI']= self.IMEI ()
        if self.gpsStatus() :
            out['gps_on']=True
        else:
            out['gps_on'] = False
        out['SIM_status']= self.SIM_Status()
        if self.SIM_Present() :
            out['IMSI'] = self.IMSI()
            if self._networkReg != None :
                out['registered'] = True
                out['network_reg']= self._networkReg
                out['PLMNID']=self._regPLMN
                out['network_name'] = self._networkName
                out['network']=self.decodePLMN(self._regPLMN)
                out['rat']  = self._rat
                out['band'] = self._band
                out['rssi'] = self._rssi
            else:
                out['registered']  = False
                out['operators'] = self.visibleOperators()

        return out


    #
    # perform a modem reset
    #
    def resetCard(self):
        modem_log.info ("RESETTING THE CARD")
        self.sendATcommand("+CFUN=1,1",True)
        modem_log.info ("Allow 20-30 sec for the card to reboot")
        # time.sleep(20)
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
        resp=self.sendATcommand("+QGPS?")
        param=self.splitResponse("+QGPS",resp[0])
        if param[0] == 0 :
            status['state'] ='off'
            return  status
        #
        # now the GPS is on let's see what have
        #
        status['state']='on'
        #
        # check NMEA port
        #
        resp=self.sendATcommand("+QGPSCFG=\"outport\"")
        param=self.splitResponse("+QGPSCFG",resp[0])
        status["NMEA_port1"]=param[0]
        status['NMEA_port2']=param[1]
        # read values
        resp=self.sendATcommand("+QGPSLOC=0")
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
        status['fix'] = True
        param=self.splitResponse("+QGPSLOC",resp[0])
        status["Time_UTC"]=param[0]
        status["Latitude"]=param[1]
        status['Longitude']=param[2]
        status["nbsat" ]=param[10]
        status["SOG_KMH"]=param[8]
        return status

    def gpsStatus(self):
        resp=self.sendATcommand("+QGPS?")
        param=self.splitResponse("+QGPS",resp[0])
        if param[0] == 0 :
            return False
        else:
            return True

    def gpsPort(self):
        resp=self.sendATcommand("+QGPSCFG=\"outport\"")
        param=self.splitResponse("+QGPSCFG",resp[0])
        return param[1]
