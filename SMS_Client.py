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

    def checkSMS(self,delete):
        req=checkSMS(deleteAfterRead=delete)
        try:
            resp=self._stub.checkSMSCommand(req)
        except grpc.RpcError as err:
            print(err)
            return None
        return resp

    def sendSMS(self,da,text):
        req=SMS()
        req.destination=da
        req.text=text
        try:
            resp=self._stub.sendSMS(req)
        except grpc.RpcError as err:
            print(err)
            return None
        return resp


def main():

    mdm=Modem_Client(sys.argv[1])
    print("====GPS Server :",sys.argv[1])
    cmd=sys.argv[2]
    if cmd == 'check' :
        msgs= mdm.checkSMS(False)
        print("Number of messages:",msgs.nbMessages)
        for m in msgs.list:
            print("Message from",m.origin,":",m.text)
    elif cmd == 'send' :
        da=sys.argv[3]
        text=sys.argv[4]
        res=mdm.sendSMS(da,text)
        print("SMS sent to:",da,"result=",res.response)






if __name__ == '__main__':
    main()
