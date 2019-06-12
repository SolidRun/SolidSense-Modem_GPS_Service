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

class GPS_Service_Client():

    def __init__(self,address) :
        self._channel= grpc.insecure_channel(address)
        self._stub= GPS_Service_pb2_grpc.GPS_ServiceStub(self._channel)

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

    gps=GPS_Service_Client(sys.argv[1])
    print("====GPS Server :",sys.argv[1]," Connected ============")
    resp=gps.getGPSPrecision()
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
