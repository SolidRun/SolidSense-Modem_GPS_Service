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




if __name__ == '__main__':
    main()
