# -*- coding: UTF-8 -*-
#-------------------------------------------------------------------------------
# Name:        GPS NMEA Reader
# Purpose:
#
# Author:      Laurent Carré
#
# Created:     09/05/2019
# Copyright:   (c) Laurent Carré Sterwen Technologies 2019
# Licence:     <your licence>
#-------------------------------------------------------------------------------
from QuectelAT_Service import *
import pynmea2

import serial
import logging

gps_serv_log=logging.getLogger('Modem_GPS_Service')

class GPS_Reader():

    def __init__(self,modem,tty="/dev/ttyUSB1"):
        # We assume that the GPS is turned on before
        self._ready=False
        self._data={}
        self._data['fix']=False
        self._fix=False
        self._tty=serial.Serial(tty,baudrate=9600,timeout=10.0)
        self._reader=pynmea2.NMEAStreamReader(self._tty,'raise')
        self._ready=True
        logging.info('GPS SERVICE: NMEA INTERFACE '+tty+' READY')



    def close(self):
        self._tty.close()

    def flush(self):
        self._tty.flushInput()

    def addSat(self,sat):
        # print("add sat:",len(self._sats),":",sat)
        if len(sat) < 1:
            return
        if len(self._sats) < self._nbsat :
            self._sats.append(int(sat))


    def readNMEAFrame(self):


        msg_rmc=None
        self._sats=[]
        self._nbsat=0

        while True :
            try:
                for msg in self._reader.next():
                    # print (msg )
                    try:
                        sentence_type= msg.sentence_type
                    except AttributeError :
                        gps_serv_log.error('GPS SERVICE: NMEA ERROR - ILL FORMED SENTENCE')
                        continue
                    if sentence_type == 'GGA':
                            # print(msg)

                            if msg.gps_qual == 0 :
                                if self._fix :
                                    gps_serv_log.debug('GPS SERVICE: GPS LOST FIX')
                                self._fix=False
                                self._data['fix']=False
                                return
                            else:
                                if not self._fix :
                                    gps_serv_log.debug('GPS SERVICE: GPS FIXED')
                                    self._fix=True
                                    self._data['fix']=True
                                self._data['hdop']=float(msg.horizontal_dil)
                                self._data['nbsat'] = int(msg.num_sats)

                    elif sentence_type == 'GSV' :
                            #first_sat=(int(msg.msg_num) - 1)*4
                            # print(msg)
                            self._nbsat=int(msg.num_sv_in_view)
                            self.addSat(msg.sv_prn_num_1)
                            self.addSat(msg.sv_prn_num_2)
                            self.addSat(msg.sv_prn_num_3)
                            self.addSat(msg.sv_prn_num_4)
                            if msg.msg_num==msg.num_messages:
                                self._data['sat_num']=self._sats
                                self._data['nbsat'] = self._nbsat
                    elif sentence_type =='RMC' :
                        # print(msg)
                        if msg.timestamp == None :
                            if self._fix:
                                gps_serv_log.debug('GPS SERVICE: GPS LOST FIX')
                                self._fix=False
                                self._data['fix'] = False
                            return
                        msg_rmc=msg

                        self._data['timestamp']= msg_rmc.timestamp.strftime("%H:%M:%S.%f")
                        self._data['latitude']= msg_rmc.latitude
                        self._data['longitude']=msg_rmc.longitude
                        self._data['date']=msg.datestamp.strftime("%d/%m/%y")
                        if msg_rmc.spd_over_grnd != None :
                            self._data['SOG']= msg_rmc.spd_over_grnd
                        else:
                            self._data['SOG']=0.0
                        self._data['COG'] = msg_rmc.true_course
                        return
            except (pynmea2.ChecksumError,pynmea2.ParseError) as err :
                gps_serv_log.error('GPS SERVICE: NMEA ERROR '+str(err))
                return


    def traceNMEA(self):
        while True:
            try:
                for msg in self._reader.next():
                    print (msg)
            except KeyboardInterrupt :
                return

    def dataPrint(self):
        print(self._data)

def main():
    logging.basicConfig()
    reader=GPS_Reader()
    reader.traceNMEA()
    reader.readNMEAFrame()
    reader.dataPrint()


if __name__ == '__main__':
    main()
