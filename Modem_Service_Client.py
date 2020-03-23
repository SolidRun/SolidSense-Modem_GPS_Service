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
        try:
            resp=self._stub.modemCommand(req)
        except grpc.RpcError as err:
            print(err)
            return None
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


def printStatus(rs):
    print("model:",rs.model,"IMEI:",rs.IMEI,"GPS ON:",rs.gps_on," SIM:",rs.SIM_status)
    if rs.SIM_status ==  'READY':
        print("IMSI:",rs.IMSI)
        if rs.registered :
            print("On:",rs.network_reg," PLMNID:",rs.PLMNID," Network:",rs.network," Radio:",rs.rat," Band:",rs.band," LAC:",rs.lac,"CI:",rs.ci, "RSSI:",rs.rssi,"dBm")
        else :
            print("Not registered - visible operators:\n",rs.operators)



def main():

    gps=Modem_Client(sys.argv[1])
    print("====GPS Server :",sys.argv[1])
    cmd=sys.argv[2]
    if len(sys.argv) > 3 :
        for arg in sys.argv[3:] :
            if len(arg) > 0 :
                cmd += ',' + arg
            else:
                break
    print("modem command:",cmd)
    resp=gps.modemCmd(cmd)
    if resp == None:
        print("Communication problem with modem_gps service")
        return

    # print("Receive frame=",resp.frameID," :",resp.response)
    if sys.argv[2]=='status' and resp.response == 'OK':
        rs=resp.status
        printStatus(rs)
        if rs.gps_on :
            resp=gps.getGPSPrecision()
            # print("Receive frame=",resp.frameID)
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
    elif sys.argv[2] == 'operator' :
        rs=resp.status
        printStatus(rs)
        print("Visible operators\n",rs.operators)






if __name__ == '__main__':
    main()
