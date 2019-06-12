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

from GPS_Reader import *

import time
import sys

# grpc modules
import grpc
import GPS_Service_pb2
import GPS_Service_pb2_grpc

class GPS_data():

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

    def getGPSPosition(self):
        self._lock.acquire()
        result=GPS_Service_pb2.GPS_Position()
        result.fix=self._data['fix']
        if result.fix :
            result.longitude=self._data['longitude']
            result.latitude=self._data['latitude']
            result.timestamp=self._data['timestamp']
        self._lock.release()
        return result

    def getGPSVector(self):
        self._lock.acquire()
        result=GPS_Service_pb2.GPS_Vector()
        result.fix=self._data['fix']
        if result.fix :
            result.longitude=self._data['longitude']
            result.latitude=self._data['latitude']
            result.timestamp=self._data['timestamp']
            result.COG=self._data['COG']
            result.SOG=self._data['SOG']
        self._lock.release()
        return result

    def getGPSPrecision(self):
        self._lock.acquire()
        result=GPS_Service_pb2.GPS_Precision()
        result.fix=self._data['fix']
        result.nbsat=self._data['nbsat']
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




class GPS_ServiceReader(GPS_Reader) :

    def __init__(self,data_block,synchro_block) :
        GPS_Reader.__init__(self)
        self._result=data_block
        self._synchro=synchro_block

    def run(self):

        while True:
            self._synchro.gpsWait()
            print("GPS start measuring")
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
        logging.debug("Running NMEA reader")
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

    def __init__(self,gps_data,synchro):
        self._gps_data=gps_data
        self._synchro=synchro


    def getPosition(self,request,context):
        logging.debug('GPS SERVICE GET POSITION REQUEST')
        self._synchro.waitStart()
        pos=self._gps_data.getGPSPosition()
        logging.debug('GPS SERVICE POSITION '+strGPSPosition(pos))
        return pos

    def getVector(self,request,context):
        logging.debug('GPS SERVICE GET VECTOR REQUEST')
        self._synchro.waitStart()
        vect=self._gps_data.getGPSVector()
        return vect

    def getPrecision(self,request,context) :
        logging.debug('GPS SERVICE GET PRECISION REQUEST')
        self._synchro.waitStart()
        pre=self._gps_data.getGPSPrecision()
        return pre


class GPS_thread(threading.Thread) :

    def __init__(self,nmea_reader) :
        threading.Thread.__init__(self)
        self._nmea_reader=nmea_reader
        self._name="NMEA Reader"

    def run(self):
        self._nmea_reader.run()


class GPS_Service_Server():

    def __init__(self,port,data_block,synchro) :
        self._synchro=synchro
        self._server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        GPS_Service_pb2_grpc.add_GPS_ServiceServicer_to_server(GPS_Servicer(data_block,synchro),self._server)
        #address = '[::]:'+str(port)
        address='0.0.0.0:'+str(port)
        logging.info('GPS SERVICE: CREATING GRPC SERVER ON:'+address)
        self._server.add_insecure_port(address)

    def start(self) :
        logging.info('GPS SERVICE: START GRPC SERVER')
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
            print("Synchro - unclock GPS")
            self._timer=time.time()
            self._waitGPS.clear()
            self._go_GPS.set()
            self._waitGPS.wait()
            print("Synchro - GPS ready")
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
    #  First we create the GPS redaing objects
    # if error no need to create the server
    #
    logging.basicConfig(level=logging.DEBUG)


    #
    #  create the NMEA reading engine
    data_block=GPS_data()
    synchro=GPS_Service_Synchro()
    #nmea_reader=GPS_nmea_simulator(sys.argv[1],data_block)
    nmea_reader=GPS_ServiceReader(data_block,synchro)
    nmea_thread=GPS_thread(nmea_reader)
    #
    # create the gRPC server
    #
    grpc_server=GPS_Service_Server(20231,data_block,synchro)

    nmea_thread.start()
    grpc_server.start()
    try:
        while True:
            time.sleep(3600.)
    except KeyboardInterrupt :
        exit()




if __name__ == '__main__':
    main()
