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
        self._ifname=ifname
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
            self._tty=serial.Serial(self._ifName,timeout=10.0)
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
        # check if SIM is present
        r=self.sendATcommand("+QSIMSTAT?")
        sim_flags=self.splitResponse("+QSIMSTAT",r[0])
        # print("SIM FLAGS=",sim_flags)
        if sim_flags[1] == 1 :
            # there is a SIM inserted
            self._SIM=True
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
        return self._SIM_STATUS
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



    def networkStatus(self):

        if not self.SIM_Ready() :
            return False
        resp=self.sendATcommand("+CREG?")
        param=self.splitResponse("+CREG",resp[0])
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
            print ("reading",fileName)
            try:
                fp=open(fileName,"r")
            except IOError as err:
                print (err)
                return
            self._operatorNames=json.load(fp)
            print ("Succefully read operators DB with:",len(self._operatorNames),"entries")
            fp.close()


    def saveOperatorNames(self,fileName)  :
        if not self.SIMPresent() :
            return
        try:
            fp=open(fileName,"w")
        except IOError as err:
            print (err)
            return
        # now retrieve all network names
        resp=self.sendATcommand("+COPN")
        self._operatorNames={}
        nbOper=0
        for r in resp:
            oper=self.splitResponse("+COPN",r)
            # print oper[0],",",oper[1]
            plmnid=oper[0]
            self._operatorNames[plmnid]=oper[1]
            nbOper=nbOper+1

        # now save in file
        json.dump(self._operatorNames,fp)
        print ("Saved",nbOper,"names in",fileName)
        fp.close()


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
                modem_log.debug ("No PLMID:",plmn)
                network=str(plmn)
        else:
            network=str(plmn)
        return network



    def logNetworkStatus(self):
        if self._networkReg == None :
            modem_log.info ("Not registered")
        else:
            modem_log.info (self._networkReg+":"+self._networkName+" PLMN:",\
                  self.decodePLMN(self._regPLMN)+" Radio:"+self._rat+" Band:"+self._band+" RSSI:"+str(self._rssi)+"dBm" )

    def logModemStatus(self,output=sys.stdout):
        modem_log.info ("Quectel modem "+self._model+self._rev)

        modem_log.info ("IMEI: %s -%d digits (incl CRC) SVN %02d" % (self._IMEI,len(self._IMEI),self._svn) )
        if self._SIM :
            modem_log.info ("SIM STATUS:"+self._SIM_STATUS)
            if self._SIM_STATUS== "READY" : modem_log.info ("SIM:"+self._IMSI)
        else :
            modem_log.info ("NO SIM Inserted"  )

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

