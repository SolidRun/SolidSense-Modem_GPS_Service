#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Laurent
#
# Created:     28/07/2019
# Copyright:   (c) Laurent 2019
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import logging
import json

local_log=logging.getLogger('Modem_GPS_Service')

modem_gps_parameters=None

def modem_gps_init_parameters():
    dir_h='/data/solidsense/modem_gps'
    fn=dir_h+'/parameters.json'
    try:
        fp=open(fn,'r')
    except IOError as err:
        local_log.info("Read parameters in:"+fn+" Err:"+str(err))
        #  initilaise with default values
        out={}
        out['modem_ctrl']='/dev/ttyUSB2'
        out['nmea_tty']='/dev/ttyUSB1'
        out['start_gps_service']=False
        out['start_gps']=False
        out['PIN']='0000'
        try:
            fp=open(fn,'w')
        except IOerror as err:
             local_log.error("Write parameters in:"+fn+" Err:"+str(err))
             raise
        json.dump(out,fp,indent=1)
        close(fp)
        modem_gps_parameters=out

def getparam(name):
    try:
        return modem_gps_parameters[name]
    except KeyError :
        return None

def main():

    pass

if __name__ == '__main__':
    main()
