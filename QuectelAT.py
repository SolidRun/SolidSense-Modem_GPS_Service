#!/usr/bin/python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        Quectel modem manager
# Purpose:
#
# Author:      Laurent Carré
#
# Created:     05/04/2019
# Copyright:   (c) Sterwen Technology 2019
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import serial
import sys,os,stat
import time
import json
import datetime


class ModemException(Exception) :
    pass

class QuectelModem():


    def __init__(self,ifName,log=False):
        self.open(ifName)
        self._logAT=log
        if self._logAT :
            self._logfp=open("asmm-atcmd.log","a")
            header="*** New session %s ****\n"% datetime.datetime.now().isoformat(' ')
            self._logfp.write(header)

        self.initialize()
        self._operatorNames=None # dictionary PLMN/Operator name
        return

    def open(self,ifName):
        try:
            self._tty=serial.Serial(ifName,timeout=10.0)
        except serial.SerialException as err:
            # print "Opening:",ifName," :",err
            raise ModemException(err)
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
            print ("Send AT command Write error",err)
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
                print ("Read at Command Error")
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
            raise ModemException("Wrong manufacturer:"+r)
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
        r=self.sendATcommand("+CIMI")
        if len(r) > 0 :
            self._SIM=True
            self._IMSI=r[0]
        else :
            self._SIM=False

    def SIMPresent(self):
        return self._SIM
    def IMEI(self):
        return self._IMEI
    def IMSI(self):
        if self._SIM :
            return self._IMSI
        else:
            return None
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

        if not self.SIMPresent() :
            return
        resp=self.sendATcommand("+CREG?")
        param=self.splitResponse("+CREG",resp[0])
        if param[1] == 1 :
            print ("registered on home operator")
            self._networkReg="HOME"
        elif param[1] == 4 :
            print ("registered on roaming" )
            self._networkReg="ROAMING"
        else:
            print ("not registered")
            self._networkReg=None
            return False

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
                print ("No PLMID:",plmn)
                network=str(plmn)
        else:
            network=str(plmn)
        return network



    def printNetworkStatus(self):
        if self._networkReg == None :
            print ("Not registered")
        else:
            print (self._networkReg,":",self._networkName,"PLMN:",\
                  self.decodePLMN(self._regPLMN),"Radio:",self._rat,"Band:",self._band )

    def printModemStatus(self,output=sys.stdout):
        print ("Quectel modem",self._model,self._rev)

        print ("IMEI: %s -%d digits (incl CRC) SVN %02d" % (self._IMEI,len(self._IMEI),self._svn) )
        if self._SIM :
            print ("SIM:",self._IMSI )
        else :
            print ("NO SIM Inserted"  )

    #
    # perform a modem reset
    #
    def resetCard(self):
        print ("RESETTING THE CARD")
        self.sendATcommand("+CFUN=1,1",True)
        print ("Allow 20-30 sec for the card to reboot")
        # time.sleep(20)

    #
    # reconfigure modem with 14 digit IMEI+SVN
    #
    def configureIMEI14SVN(self,svn):
        # build the command or writing IMEI
        cmd="+EGMR=1,7,\"%s\"" % self._IMEI[:14]
        print ("Setting 14 digits IMEI:", self._IMEI[:14]  )
        self.sendATcommand(cmd,True)
        # r= self.sendATcommand("+EGMR=0,9",True)
        # print r[0]
        # configure new IMEI+SVN
        cmd=  "+QSVN=\"%s\""  % svn
        print ("Configuring IMEI+SVN:",svn )
        self.sendATcommand(cmd,True)
        # reset the card
        self.resetCard()
    #
    # reconfigure modem with 15 digits
    #
    def configureIMEI15(self,imei):
        if len(imei) != 15 :
            print ("IMEI wrong nb of digits:",len(imei) )
            return
        cmd="+EGMR=1,7,\"%s\"" % imei
        print ("Programming new IMEI 15 digits:",imei )
        self.sendATcommand(cmd,True)
        # reset card
        self.resetCard()
    #
    #  display visible operators
    #
    def displayOperators(self):
        access = { 0 : 'Unknown', 1 : 'Available', 2:'Current', 3:'Forbidden'}
        rat = {0:'GSM',2:'UTRAN',3:'GSM/GPRS',4:'3G HSDPA',5:'3G HSUPA',
          6:'3G HSDPA/HSUPA',7:'LTE',100:'CDMA'}
        print ("Looking for operators....." )
        resp=self.sendATcommand("+COPS=?")
        oper=resp[0].split('(')
        print ("Operators visible by the modem")
        for o in oper[1:] :
            # print o
            fields=o.split(',')
            if len(fields) < 5 :
                print( "Strange operator:",o )
                continue
            a=int(fields[0])
            o=fields[1][1:len(fields[1])-1]
            p=int(fields[3][1:len(fields[3])-1] )
            ip=fields[4].find(')')
            #print fields[4],ip
            r=int(fields[4][:ip])
            try:
                print (o,":",access[a],"PLMN:",self.decodePLMN(p)," AT:",rat[r])
            except KeyError :
                continue

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

    def printGpsStatus(self):
        resp=self.sendATcommand("+QGPS?")
        param=self.splitResponse("+QGPS",resp[0])
        if param[0] == 0 :
            print ("GPS is turned off" )
            return
        #
        # now the GPS is on let's see what have
        #
        print ("gps is on")
        #
        # check NMEA port
        #
        resp=self.sendATcommand("+QGPSCFG=\"outport\"")
        param=self.splitResponse("+QGPSCFG",resp[0])
        print ("NMEA output port:",param[0],",",param[1] )
        # read values
        resp=self.sendATcommand("+QGPSLOC=0",resp[0])
        param=self.splitResponse("+QGPSLOC",resp[0])
        print ("Time UTC:",param[0][0:2],":", param[0][2:4],":",param[0][4:6]  )
        print ("Position:",param[1],",",param[2])
        print ("number of satellites:" ,param[10])
        print ("Speed on ground (km/h):",param[8] )

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

