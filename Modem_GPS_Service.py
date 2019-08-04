#!/usr/bin/python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        GPS_nmea.py
# Purpose:
#
# Author:      Laurent Carré
#
# Created:     10/04/2019
# Copyright:   (c) Laurent Carré - Sterwen Technology 2019
# Licence:     <your licence>
#-------------------------------------------------------------------------------

from concurrent import futures
import logging
import threading
import time
import sys

# grpc modules
import grpc
import GPS_Service_pb2
import GPS_Service_pb2_grpc

from GPS_Reader import *
from Modem_GPS_Parameters import *
from Modem_Service import *

gps_log=logging.getLogger('Modem_GPS_Service')

class GPS_data():

    position_fields=(('longitude',float),('latitude',float),('timestamp',str))
    vector_fields =(('longitude',float),('latitude',float),('timestamp',str),('COG',float),('SOG',float))


    def __init__(self):
        self._lock= threading.Lock()
        self._data={}

    def setData(self,data) :
        #print("SET DATA===\n",data)
        self._lock.acquire()
        for key in data.keys():
            self._data[key]=data[key]
        self._lock.release()
        #print(self._data)

    def buildResult(self,result,data_set):
        for d in data_set:
            try:
                v=self._data[d[0]]
            except KeyError:
                result.fix=False
                return
            if type(v) != d[1] :
                result.fix=False
                return
            object.__setattr__(result,d[0],v)

    def getGPSPosition(self):
        self._lock.acquire()
        result=GPS_Service_pb2.GPS_Position()
        result.fix=self._data['fix']
        if result.fix :
            self.buildResult(result,GPS_data.position_fields)
        self._lock.release()
        return result

    def getGPSVector(self):
        self._lock.acquire()
        result=GPS_Service_pb2.GPS_Vector()
        result.fix=self._data['fix']
        if result.fix :
            self.buildResult(result,GPS_data.vector_fields)
        self._lock.release()
        return result

    def getGPSPrecision(self):
        self._lock.acquire()
        result=GPS_Service_pb2.GPS_Precision()
        result.fix=self._data['fix']
        try:
            result.nbsat=self._data['nbsat']
        except KeyError :
            # in that case no frame has been received
            result.fix=False
            result.nbsat=0
            return result

        for sat in self._data['sat_num']:
            result.sat_num.append(sat)
        if result.fix :
            result.hdop=self._data['hdop']
            result.timestamp=self._data['timestamp']
            result.date=self._data['date']
        self._lock.release()
        return result

    def printData(self):
        print(self._data)

def strGPSPosition(pos):
    str_res="GPS Fixed:"+str(pos.fix)
    if pos.fix :
        str_res=str_res+" Time:"+str(pos.timestamp)+" LAT:"+str(pos.latitude)+" LONG:"+str(pos.longitude)
    return str_res

def dictToResult(dict,res) :
    for v in dict.items():
        object.__setattr__(res,v[0],v[1])



class GPS_ServiceReader(GPS_Reader) :

    def __init__(self,data_block,synchro_block) :

        GPS_Reader.__init__(self)
        self._result=data_block
        self._synchro=synchro_block

    def run(self):

        while True:
            self._synchro.gpsWait()
            logging.info("GPS start measuring")
            self.runOnce()
            self._synchro.gpsReady()
            self._synchro.checkTimer()

    '''
    def runContinuous(self):
        while self._continuous:
            try:
                self.flush()
                self.readNMEAFrame()
            except KeyboardInterrupt :
                exit()
            self._result.setData(self._data)
            if self._fix :
                time.sleep(.5)
            else:
                time.sleep(5.)
            # self._result.printData()
    '''

    def runOnce(self):
        self.flush()
        self.readNMEAFrame()
        self._result.setData(self._data)



class GPS_nmea_simulator(GPS_Reader) :

    def __init__(self,file,result):
         # first check that the GPS is turned on
        self._ready=False
        self._data={}
        self._data['fix']=False
        self._result=result
        self._fix=False
        self._fd=open(file,"r")
        self._reader=pynmea2.NMEAStreamReader(self._fd)
        self._ready=True
        logging.info('GPS SERVICE: NMEA INTERFACE '+file+' READY')

    def run(self):
        gps_log.debug("Running NMEA reader")
        while True:
            try:
                self.readNMEAFrame()
            except KeyboardInterrupt :
                exit()
            self._result.setData(self._data)
            # self._result.printData()
            try:
                time.sleep(10.)
            except KeyboardInterrupt:
                exit()



class GPS_Servicer(GPS_Service_pb2_grpc.GPS_ServiceServicer) :

    def __init__(self,gps_data,synchro,modem):
        self._gps_data=gps_data
        self._synchro=synchro
        self._frameID=0
        self._modem=modem



    def getPosition(self,request,context):
        gps_log.debug('GPS SERVICE GET POSITION REQUEST')
        self._synchro.waitStart()
        pos=self._gps_data.getGPSPosition()
        gps_log.debug('GPS SERVICE POSITION '+strGPSPosition(pos))
        return pos

    def getVector(self,request,context):
        gps_log.debug('GPS SERVICE GET VECTOR REQUEST')
        self._synchro.waitStart()
        vect=self._gps_data.getGPSVector()
        gps_log.debug('GPS SERVICE POSITION (V) '+strGPSPosition(vect))
        return vect

    def getPrecision(self,request,context) :
        gps_log.debug('GPS SERVICE GET PRECISION REQUEST')
        self._synchro.waitStart()
        pre=self._gps_data.getGPSPrecision()
        pre.frameID=self._frameID
        self._frameID= self._frameID + 1
        gps_log.debug('GPS SERVICE GET PRECISION '+pre.date+' '+pre.timestamp+" ID:"+str(pre.frameID) )
        return pre

    def modemCommand(self,request,context):
        cmd=request.command
        gps_log.debug('MODEM COMMAND:'+cmd)
        resp=GPS_Service_pb2.ModemResp()
        resp.frameID=self._frameID
        self._frameID= self._frameID + 1
        if cmd == "test" :
            resp.response="DUMMY FOR TEST"
        else:
            rm=self._modem.executeCommand(cmd)
            resp.response=rm[0]
            if rm[0] == "OK" :
               dictToResult(rm[1],resp.status)

        gps_log.debug('MODEM COMMAND SERVICE RESPONSE:'+resp.response)
        return resp


class GPS_thread(threading.Thread) :

    def __init__(self,nmea_reader) :
        threading.Thread.__init__(self)
        self._nmea_reader=nmea_reader
        self._name="NMEA Reader"

    def run(self):
        self._nmea_reader.run()


class GPS_Service_Server():

    def __init__(self,data_block,synchro,modem_server) :
        self._synchro=synchro
        self._server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        GPS_Service_pb2_grpc.add_GPS_ServiceServicer_to_server(GPS_Servicer(data_block,synchro,modem_server),self._server)
        l_address = getparam('address')
        port=getparam('port')
        address=l_address+':'+str(port)
        gps_log.info('GPS SERVICE: CREATING GRPC SERVER ON:'+address)
        self._server.add_insecure_port(address)

    def start(self) :
        gps_log.info('GPS SERVICE: START GRPC SERVER')
        self._server.start()


class GPS_Service_Synchro() :


    def __init__(self):
        self._go_GPS=threading.Event()
        self._waitGPS= threading.Event()
        self._timer=time.time()
        self._state=0


    def stop(self):
        print("Synchro timer expire")
        if self._state == 1 :
            self._go_GPS.clear()
            self._state=0

    def waitStart(self):
        if self._state == 0 :
            # print("Synchro - unclock GPS")
            self._timer=time.time()
            self._waitGPS.clear()
            self._go_GPS.set()
            self._waitGPS.wait()
            # print("Synchro - GPS ready")
            self._state=1
        else:
            self._timer=time.time()

    def gpsReady(self):
        self._waitGPS.set()

    def gpsWait(self):
        self._go_GPS.wait()

    def checkTimer(self):
        if time.time() - self._timer > 10.:
            self.stop()




def main():
    #
    #
    logging.basicConfig(level=logging.DEBUG,format='%(asctime)s - %(message)s',file=sys.stdout)
    #
    modem_gps_init_parameters()
    # adjust log level
    gps_log.setLevel(getLogLevel())
    # print("Logging level:",gps_log.getEffectiveLevel())
    #
    #  check the status of the modem and perform init sequence
    #

    ms=Modem_Service()
    #
    # check if the interface is ready
    #
    if not ms.checkCard() :
        gps_log.critical("MODEM CARD NOT PRESENT OR NOT READY:"+ms.controlIf())
        exit(2)
    #  now initialise the modem
    try:
        ms.performInit()
    except :
        gps_log.critical("ERROR DURING MODEM INITIALIZATION => STOP")
        exit(2)

    # check if we have someting else to do
    if getparam('start_gps_service') == False:
        # check if we need to start the GPS anyway
        if getparam('gps_start'):
            ms.startGPS()
        # nothing else to do
        gps_log.info("MODEM READY - NO SERVICE NEEDED - EXITING")
        exit(0) # no restart

    #  Now we have to start the gRPC micro-service
    #
    ms.startGPS()
    ms.close()
    #
    #  create the NMEA reading engine
    data_block=GPS_data()
    synchro=GPS_Service_Synchro()
    # nmea_reader=GPS_nmea_simulator(sys.argv[1],data_block)
    try:
        nmea_reader=GPS_ServiceReader(data_block,synchro)
    except :
        gps_log.critical("CANNOT INITIALIZE GPS READER EXITING...")
        exit(2)

    nmea_thread=GPS_thread(nmea_reader)
    #
    # create the gRPC server
    #
    grpc_server=GPS_Service_Server(data_block,synchro,ms)

    nmea_thread.start()
    grpc_server.start()
    try:
        while True:
            time.sleep(3600.)
    except KeyboardInterrupt :
        exit(0)




if __name__ == '__main__':
    main()
