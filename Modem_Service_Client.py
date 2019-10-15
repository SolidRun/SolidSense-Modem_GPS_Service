#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Laurent
#
# Created:     05/05/2019
# Copyright:   (c) Laurent 2019
# Licence:     <your licence>
#-------------------------------------------------------------------------------

# grpc modules
import grpc
from GPS_Service_pb2 import *
import GPS_Service_pb2_grpc

import sys

class Modem_Client():

    def __init__(self,address) :
        self._channel= grpc.insecure_channel(address)
        self._stub= GPS_Service_pb2_grpc.GPS_ServiceStub(self._channel)

    def modemCmd(self,cmd):
        req=ModemCmd(command=cmd)
        resp=self._stub.modemCommand(req)
        return resp

    def getGPSPosition(self):
        req=PositionSpec(spec=PositionSpec.P2D)
        resp=self._stub.getPosition(req)
        return resp

    def getGPSVector(self):
        req=PositionSpec(spec=PositionSpec.P2D)
        resp=self._stub.getVector(req)
        return resp

    def getGPSPrecision (self):
        req=PositionSpec(spec=PositionSpec.P2D)
        resp=self._stub.getPrecision(req)
        return resp


def main():

    gps=Modem_Client(sys.argv[1])
    print("====GPS Server :",sys.argv[1]," Connected ============")
    resp=gps.modemCmd(sys.argv[2])
    print("Receive frame=",resp.frameID," :",resp.response)
    if sys.argv[2]=='status' and resp.response == 'OK':
        rs=resp.status
        print("model:",rs.model,"IMEI:",rs.IMEI,"GPS ON:",rs.gps_on," SIM:",rs.SIM_status)
        if rs.SIM_status ==  'READY':
            print("IMSI:",rs.IMSI)
            if rs.registered :
                print("On:",rs.network_reg," Network:",rs.network," Radio:",rs.rat,"Band:",rs.band," RSSI:",rs.rssi,"dBm")
            else :
                print("Not registered - visible operators:\n",rs.operators)
        if rs.gps_on :
            resp=gps.getGPSPrecision()
            print("Receive frame=",resp.frameID)
            if resp.fix :
                print("GPS FIXED date:",resp.date, "time:",resp.timestamp)
                resp=gps.getGPSVector()
                print("LAT:",resp.latitude,"LONG:",resp.longitude,"SOG:",resp.SOG,"COG:",resp.COG)
            else:
                print("GPS Not fixed")
                res="Satellite in view:"+str(resp.nbsat)+" ["
                for n in resp.sat_num :
                    res= res+str(n)+","
                res=res+"]"
                print (res)





if __name__ == '__main__':
    main()