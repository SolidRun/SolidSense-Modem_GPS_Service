# Modem_GPS_Service

systemd service to be used for controlling the modem and reading GPS

This is a gRPC based micro service allowing to control the Modem-GPS card from the SolidSEnse gateway.
It also allows the initialization of the card during system startup with the parametrs given in the configuration file

# Modem control

The service can perform the follwing action on startup:
1) Enter the PIN code protecting the SIM card
2) Start the GPS

At any time the service is responding to a status request by answering the full state of the modem:
    Hardware/Software version and IMEI
    SIM Presence and characteristics
    Network and Radio Status

#gRPC server

Listening address and port are configurable. default 0.0.0.0:20231

GPS RPC
1) getPrecision: return the the fix state and GPS precision info + date and time
2) getPosition:return the GPS position
3) getVector: return the position and displacement vector

If the GPS is not fixed then only limited information from getPrecision are available, like the number of satellites

Modem RPC
1) modemCommand: execute the command in the argument message and returns the full status. Currently on the the 'status' command is implemented

Full gRPC interface in the GPS_Service.proto file

#Configuration file

the configuration file is in JSON format (parameter.json)  located in /data/solidsense/modem_gps/.
A default version is created when no file is existing

start_gps_service   :if False (default), no rRPC server is launched, only modem intialisation is performed
start_gps           :initialisation of the GPS if no service is launched. The gPS is turned on in any case with the service

