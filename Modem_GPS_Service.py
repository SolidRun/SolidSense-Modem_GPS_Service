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
import queue

# grpc modules
import grpc
import GPS_Service_pb2
import GPS_Service_pb2_grpc

from GPS_Reader import *
from Modem_GPS_Parameters import *
from Modem_Service import *

gps_log=None
modem_gps_version="2.0.0"

grpc_server=None
exit_flag= -1

class GPS_data():

    position_fields=(('longitude',float),('latitude',float),('gps_time',str))
    vector_fields =(('longitude',float),('latitude',float),('gps_time',str),('altitude',float),('COG',float),('SOG',float))


    def __init__(self):
        self._lock= threading.Lock()
        self._data={}

    def setData(self,data) :
        # print("SET DATA===\n",data)
        self._lock.acquire()
        for key in data.keys():
            self._data[key]=data[key]
        self._lock.release()
        # print(self._data)

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
            # correction bug#67
            # need to release the lock
            self._lock.release()
            return result

        for sat in self._data['sat_num']:
            result.sat_num.append(sat)
        if result.fix :
            result.hdop=self._data['hdop']
            result.gps_time=self._data['gps_time']
            result.date=self._data['date']
        self._lock.release()
        return result

    def printData(self):
        print(self._data)

def strGPSPosition(pos):
    str_res="GPS Fixed:"+str(pos.fix)
    if pos.fix :
        str_res=str_res+" Time:"+str(pos.gps_time)+" LAT:"+str(pos.latitude)+" LONG:"+str(pos.longitude)
    return str_res

def dictToResult(dict_resp,res) :
    for attr,val in dict_resp.items():
        try:
            object.__setattr__(res,attr,val)
        except (ValueError, TypeError) :
            gps_log.error("Error on gRPC encoding for attribute:"+attr)
            print(attr,"=",val,type(val))



class GPS_ServiceReader(GPS_Reader) :

    def __init__(self,data_block,synchro_block) :

        GPS_Reader.__init__(self)
        self._result=data_block
        self._synchro=synchro_block
        self._continuous=False

    def run(self):

        while True:
            if self._synchro.gpsWait():
                # we need to exit the loop
                gps_log.info("GPS Thread Stop request received")
                break   # stop the thread
            if self._continuous :
                self.runContinuous()
            else:
                gps_log.debug("GPS start measuring")
                self.runOnce()
                self._synchro.gpsReady()
                self._synchro.checkTimer()
            if self._synchro.stopThread() :
                gps_log.info("GPS Thread Stop request received")
                break   # stop the thread


    def setContinuous(self,send_queue,rules):
        gps_log.debug("GPS Reader set in continuous mode param:"+str(rules))
        self._continuous=True
        self._last=False
        self._queue=send_queue
        self._rules=rules
        self._fixtime=time.time()
        self._nofixtime=self._fixtime
        self._movingtime=self._fixtime
        self._reportime=self._fixtime
        self._refpos=None

        #
        # the following values shall be fixed via rules
        #
        self._fixtime_interval=rules.get('fix_interval',10.) # report every minutes when not moving
        self._nofixtime_interval= rules.get('nofix_interval',60.) # report every 30mn if no fix
        self._distance = rules.get('distance',100.0) # reports every 100m when moving
        self._min_speed=self._distance/self._fixtime_interval

    def stopContinuous(self):
        self._last=True
        gps_log.debug("GPS Reader request to non continuous mode")


    def pushPosition(self):
        result=GPS_Service_pb2.GPS_Vector()
        result.fix=self._data['fix']
        if result.fix :
            self.buildResult(result,GPS_data.vector_fields)
        try:
            self._queue.put(result)
        except queue.Full :
            gps_log.critical("GPS send queue FULL")

        gps_log.debug("Pushing one position in the queue")
        if self._last:
            self._continuous=False
            gps_log.debug("GPS Reader stop continuous mode")
            self._synchro.stop()
        return result


    def runContinuous(self):

        self.readNMEAFrame()

        t=time.time()
        if self._fix :
            speed=self._data['SOG']
            speed_ms=speed*(1852.0/3600.0)
            if speed_ms < self._min_speed :
                # check time for
                if t-self._fixtime >= self._fixtime_interval :
                    self.pushPosition()
                    self._fixtime = t
            else:

                dist=speed_ms*(t-self._movingtime)
                if dist >= self._distance :
                    self.pushPosition()
                    self._movingtime=t

        else:
            if (t-self._nofixtime) >= self._nofixtime_interval :
                self.pushPosition()
                self._nofixtime=t

        if (t-self._reportime) >= 10. :
            self._result.setData(self._data)
            self._reportime=t


    def runOnce(self):
        self.flush()
        self.readNMEAFrame()
        self._result.setData(self._data)

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

    def __init__(self,gps_data,synchro,modem,reader):
        self._gps_data=gps_data
        self._synchro=synchro
        self._frameID=0
        self._modem=modem
        self._reader=reader



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
        gps_log.debug('GPS SERVICE GET PRECISION '+pre.date+' '+pre.gps_time+" ID:"+str(pre.frameID) )
        return pre

    def modemCommand(self,request,context):
        global grpc_server,exit_flag
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
            elif rm[0] == "STOP":
                self._synchro.setStopThread()
                grpc_server.stop()
                exit_flag=0
            elif rm[0]== "RESTART":
                self._synchro.setStopThread()
                grpc_server.stop()
                exit_flag=2


        gps_log.debug('MODEM COMMAND SERVICE RESPONSE:'+resp.response)
        return resp

    def streamGPS(self,request,context) :
        gps_log.debug("GPS SERVICE STREAM READING")
        try:
            cmd=json.loads(request.command)
        except ValueError as e:
            gps_log.error("GPS service: Error decoding streaming parameters")
            cmd={}

        # create the queue
        gps_queue=queue.Queue(20)
        self._synchro.setGPSContinuous()
        self.stop_flag=False
        self._reader.setContinuous(gps_queue,cmd)
        self._synchro.startContinuous()
        while True:

            if self.stop_flag :
                # empty the queue
                # to be done
                gps_log.debug("Stop GPS streaing flag detected")
                while not gps_queue.empty() :
                    pos=gps_queue.get()
                    yield pos
                gps_log.debug("Position queue is now empty")
                return
            else:
                pos=gps_queue.get()
                yield pos

    def stopStream(self,request,context):
        gps_log.debug("GPS SERVICE STOP STREAM READING")
        # self._synchro.stop()
        self._reader.stopContinuous()
        self.stop_flag=True
        # the system runs until the next message is pushed
        resp=GPS_Service_pb2.ModemResp()
        resp.response="OK"
        return resp
    '''
    SMS related commands
    '''
    def sendSMS(self,request,context):
        gps_log.debug("MODEM SERVICE SEND SMS")
        result=self._modem.sendSMS(request.destination,request.text)
        resp=GPS_Service_pb2.ModemResp()
        gps_log.debug("SMS sending to:"+request.destination+" result="+result)
        resp.frameID=self._frameID
        self._frameID= self._frameID + 1
        resp.response=result
        return resp

    def checkSMSCommand(self,request,context):
        gps_log.debug("MODEM SERVICE CHECK SMS")
        msgs=self._modem.checkSMS(request.deleteAfterRead)
        resp=GPS_Service_pb2.receivedSMSList()
        if resp == None :
             resp.nbMessages=0
             return resp

        resp.nbMessages=len(msgs)
        if resp.nbMessages > 0 :
            for m in msgs:
                msg=GPS_Service_pb2.receivedSMS()
                msg.origin=m['origin']
                msg.sms_time=m['sms_time']
                msg.text=m['text']
                resp.list.append(msg)
        return resp


class GPS_thread(threading.Thread) :

    def __init__(self,nmea_reader) :
        threading.Thread.__init__(self)
        self._nmea_reader=nmea_reader
        self._name="NMEA Reader"

    def run(self):
        self._nmea_reader.run()


class GPS_Service_Server():

    def __init__(self,data_block,synchro,modem_server,reader) :
        self._synchro=synchro
        self._server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        GPS_Service_pb2_grpc.add_GPS_ServiceServicer_to_server(GPS_Servicer(data_block,synchro,modem_server,reader),self._server)
        l_address = getparam('address')
        port=getparam('port')
        address=l_address+':'+str(port)
        gps_log.info('GPS SERVICE: CREATING GRPC SERVER ON:'+address)
        self._server.add_insecure_port(address)
        self._endEvent=threading.Event()

    def start(self) :
        gps_log.info('GPS SERVICE: START GRPC SERVER')
        self._server.start()

    def stop(self):
        gps_log.info('GPS SERVICE: STOP GRPC SERVER')
        self._finalEnd=self._server.stop(1.0)
        self._endEvent.set()

    def waitEnd(self):
        self._endEvent.wait()
        # print("End event received")
        self._finalEnd.wait()
        # print("Final event received")


class GPS_Service_Synchro() :


    def __init__(self):
        self._go_GPS=threading.Event()
        self._waitGPS= threading.Event()
        self._timer=time.time()
        self._state=0
        self._stopThread=False


    def stop(self):
        # print("Synchro timer expire")
        if self._state != 0 :
            self._go_GPS.clear()
            self._state=0

    def waitStart(self):
        # unblock the GPS and wait for data
        if self._state == 0 :
            # print("Synchro - unclock GPS")
            self._timer=time.time()
            self._waitGPS.clear()
            self._go_GPS.set()
            self._waitGPS.wait()
            # print("Synchro - GPS ready")
            self._state=1
        elif self._state == 2:
            return
        else:
            self._timer=time.time()

    def gpsReady(self):
        # signal that the GPS measures are ready
        self._waitGPS.set()

    def gpsWait(self):
        # block the GPS thread
        self._go_GPS.wait()
        return self._stopThread

    def checkTimer(self):
        if time.time() - self._timer > 10.:
            self.stop()

    def setStopThread(self):
        self._stopThread=True
        if self._state == 0:
            self._go_GPS.set() #unlock the GPS thread

    def stopThread(self):
        return self._stopThread

    def setGPSContinuous(self):
        if self._state == 0:
            self._state=2
            return
        self.stop()
        self._waitGPS.wait()
        self._state=2

    def startContinuous(self):
        self._go_GPS.set()



def OkModem():
    global gps_log
    gps_log.critical("MODEM_OK")

def main():
    #
    global grpc_server
    global gps_log
    #

    '''
    f_log= logging.Formatter("%(asctime)s | [%(levelname)s] %(name)s@%(filename)s:%(lineno)d:%(message)s")
    l_handler= logging.StreamHandler()
    l_handler.setFormatter(f_log)

    gps_log.addHandler(l_handler)
    gps_log.setLevel(logging.DEBUG)
    '''
    logging.basicConfig(level=logging.DEBUG,format="%(asctime)s [%(levelname)s]:%(message)s",stream=sys.stdout)
    gps_log=logging.getLogger('Modem_GPS_Service')
    #
    modem_gps_init_parameters(gps_log)
    # adjust log level
    gps_log.setLevel(getLogLevel())
    # print("Logging level:",gps_log.getEffectiveLevel())
    gps_log.info("Start Modem GPS Micro service version "+modem_gps_version)
    #
    #  check the status of the modem and perform init sequence
    #

    ms=Modem_Service()
    #
    # check if the interface is ready
    #
    if not ms.checkCard() :
        gps_log.critical("MODEM CARD NOT PRESENT OR NOT READY:"+ms.controlIf())
        OkModem()
        exit(2)
    #  now initialise the modem
    nb_retry = 0
    init_final=True
    try:
        while nb_retry < 4 :
            gps_log.info("Starting Modem initialisation sequence attempt:"+str(nb_retry))
            if ms.performInit() :
                nb_retry += 1
            else:
                init_final=False
                break
        if init_final :
            gps_log.critical("MODEM UNABLE TO INITIALIZE => RESET")
            ms.modemReset()
            OkModem()
            exit(2)
    except :
        gps_log.critical("FATAL ERROR DURING MODEM INITIALIZATION => STOP")
        OkModem()
        exit(2)

    OkModem()
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
    grpc_server=GPS_Service_Server(data_block,synchro,ms,nmea_reader)

    nmea_thread.start()
    grpc_server.start()
    try:
        grpc_server.waitEnd()
    except KeyboardInterrupt :
        exit(0)
    nmea_thread.join()
    gps_log.info("GPS SERVICE EXITING WITH CODE:"+str(exit_flag))
    exit(exit_flag)




if __name__ == '__main__':
    main()
