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
    global modem_gps_parameters
    dir_h=getDataDir()
    fn=dir_h+'/parameters.json'
    try:
        fp=open(fn,'r')
    except (IOError, FileNotFoundError) as err:
        local_log.info("Read parameters in:"+fn+" Err:"+str(err))
        #  initilaise with default values
        default_param()
        try:
            fp=open(fn,'w')
        except IOError as err:
            local_log.error("Write parameters in:"+fn+" Err:"+str(err))
            raise
        json.dump(modem_gps_parameters,fp,indent=1)
        fp.close()
        return
    try:
        modem_gps_parameters=json.load(fp)
    except Exception as err:
        local_log.error("Error decoding parameter file (running on default):"+str(err))
        default_param()
    # print(modem_gps_parameters)
    fp.close()

def default_param():
    global modem_gps_parameters
    out={}
    out['modem_ctrl']='/dev/ttyUSB2'
    out['nmea_tty']='/dev/ttyUSB1'
    out['start_gps_service']=True
    out['start_gps']=False
    out['PIN']='0000'
    out['address']='0.0.0.0'
    out['port']=20231
    out['operatorsDB']="operatorsDB"
    out['trace']= "info"
    out['roaming']=True

    modem_gps_parameters=out

def getparam(name):
    try:
        return modem_gps_parameters[name]
    except KeyError :
        return None

debug_level_def={ 'debug':logging.DEBUG, 'info': logging.INFO , 'warning':logging.WARNING, 'error':logging.ERROR, 'critical':logging.CRITICAL}
def getLogLevel():
    try:
        level_str= modem_gps_parameters['trace']
    except KeyError :
        return logging.DEBUG
    level_str=level_str.lower()
    try:
        level=debug_level_def[level_str]
    except KeyError :
        return logging.DEBUG
    # print("debug:",level_str,level)
    return level

def getDataDir():
    return "/data/solidsense/modem_gps"

def buildFileName(param):
    fn=getparam(param)
    return getDataDir()+'/'+fn

def main():

    pass

if __name__ == '__main__':
    main()
