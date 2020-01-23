# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: GPS_Service.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='GPS_Service.proto',
  package='',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=_b('\n\x11GPS_Service.proto\"e\n\x0cGPS_Position\x12\x0b\n\x03\x66ix\x18\x01 \x01(\x08\x12\x11\n\ttimestamp\x18\x02 \x01(\t\x12\x10\n\x08latitude\x18\x03 \x01(\x02\x12\x11\n\tlongitude\x18\x04 \x01(\x02\x12\x10\n\x08\x61ltitude\x18\x05 \x01(\x02\"k\n\nGPS_Vector\x12\x0b\n\x03\x66ix\x18\x01 \x01(\x08\x12\x11\n\ttimestamp\x18\x02 \x01(\t\x12\x10\n\x08latitude\x18\x03 \x01(\x02\x12\x11\n\tlongitude\x18\x04 \x01(\x02\x12\x0b\n\x03\x43OG\x18\x05 \x01(\x02\x12\x0b\n\x03SOG\x18\x06 \x01(\x02\"|\n\rGPS_Precision\x12\x0f\n\x07\x66rameID\x18\n \x01(\r\x12\x0b\n\x03\x66ix\x18\x01 \x01(\x08\x12\r\n\x05nbsat\x18\x02 \x01(\r\x12\x11\n\ttimestamp\x18\x03 \x01(\t\x12\x0c\n\x04\x64\x61te\x18\x04 \x01(\t\x12\x0f\n\x07sat_num\x18\x05 \x03(\r\x12\x0c\n\x04hdop\x18\x06 \x01(\x02\"j\n\x0cPositionSpec\x12+\n\x04spec\x18\x01 \x01(\x0e\x32\x1d.PositionSpec.PositionSpecDef\"-\n\x0fPositionSpecDef\x12\x07\n\x03P2D\x10\x00\x12\x07\n\x03P3D\x10\x01\x12\x08\n\x04\x42\x65st\x10\x02\"\x1b\n\x08ModemCmd\x12\x0f\n\x07\x63ommand\x18\x01 \x01(\t\"\x91\x02\n\x0bModemStatus\x12\r\n\x05model\x18\x01 \x01(\t\x12\x0c\n\x04IMEI\x18\x02 \x01(\t\x12\x0e\n\x06gps_on\x18\x03 \x01(\x08\x12\x12\n\nSIM_status\x18\x04 \x01(\t\x12\x0c\n\x04IMSI\x18\x05 \x01(\t\x12\x12\n\nregistered\x18\x06 \x01(\x08\x12\x13\n\x0bnetwork_reg\x18\x07 \x01(\t\x12\x0e\n\x06PLMNID\x18\x08 \x01(\r\x12\x14\n\x0cnetwork_name\x18\t \x01(\t\x12\x0f\n\x07network\x18\n \x01(\t\x12\x0b\n\x03lac\x18\x0f \x01(\r\x12\n\n\x02\x63i\x18\x10 \x01(\r\x12\x0b\n\x03rat\x18\x0b \x01(\t\x12\x0c\n\x04\x62\x61nd\x18\x0c \x01(\t\x12\x0c\n\x04rssi\x18\r \x01(\x11\x12\x11\n\toperators\x18\x0e \x01(\t\"L\n\tModemResp\x12\x0f\n\x07\x66rameID\x18\x01 \x01(\r\x12\x10\n\x08response\x18\x02 \x01(\t\x12\x1c\n\x06status\x18\x03 \x01(\x0b\x32\x0c.ModemStatus2\xc1\x01\n\x0bGPS_Service\x12-\n\x0bgetPosition\x12\r.PositionSpec\x1a\r.GPS_Position\"\x00\x12)\n\tgetVector\x12\r.PositionSpec\x1a\x0b.GPS_Vector\"\x00\x12/\n\x0cgetPrecision\x12\r.PositionSpec\x1a\x0e.GPS_Precision\"\x00\x12\'\n\x0cmodemCommand\x12\t.ModemCmd\x1a\n.ModemResp\"\x00\x62\x06proto3')
)



_POSITIONSPEC_POSITIONSPECDEF = _descriptor.EnumDescriptor(
  name='PositionSpecDef',
  full_name='PositionSpec.PositionSpecDef',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='P2D', index=0, number=0,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='P3D', index=1, number=1,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='Best', index=2, number=2,
      serialized_options=None,
      type=None),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=420,
  serialized_end=465,
)
_sym_db.RegisterEnumDescriptor(_POSITIONSPEC_POSITIONSPECDEF)


_GPS_POSITION = _descriptor.Descriptor(
  name='GPS_Position',
  full_name='GPS_Position',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='fix', full_name='GPS_Position.fix', index=0,
      number=1, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='timestamp', full_name='GPS_Position.timestamp', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='latitude', full_name='GPS_Position.latitude', index=2,
      number=3, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='longitude', full_name='GPS_Position.longitude', index=3,
      number=4, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='altitude', full_name='GPS_Position.altitude', index=4,
      number=5, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=21,
  serialized_end=122,
)


_GPS_VECTOR = _descriptor.Descriptor(
  name='GPS_Vector',
  full_name='GPS_Vector',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='fix', full_name='GPS_Vector.fix', index=0,
      number=1, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='timestamp', full_name='GPS_Vector.timestamp', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='latitude', full_name='GPS_Vector.latitude', index=2,
      number=3, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='longitude', full_name='GPS_Vector.longitude', index=3,
      number=4, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='COG', full_name='GPS_Vector.COG', index=4,
      number=5, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='SOG', full_name='GPS_Vector.SOG', index=5,
      number=6, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=124,
  serialized_end=231,
)


_GPS_PRECISION = _descriptor.Descriptor(
  name='GPS_Precision',
  full_name='GPS_Precision',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='frameID', full_name='GPS_Precision.frameID', index=0,
      number=10, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='fix', full_name='GPS_Precision.fix', index=1,
      number=1, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='nbsat', full_name='GPS_Precision.nbsat', index=2,
      number=2, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='timestamp', full_name='GPS_Precision.timestamp', index=3,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='date', full_name='GPS_Precision.date', index=4,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='sat_num', full_name='GPS_Precision.sat_num', index=5,
      number=5, type=13, cpp_type=3, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='hdop', full_name='GPS_Precision.hdop', index=6,
      number=6, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=233,
  serialized_end=357,
)


_POSITIONSPEC = _descriptor.Descriptor(
  name='PositionSpec',
  full_name='PositionSpec',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='spec', full_name='PositionSpec.spec', index=0,
      number=1, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _POSITIONSPEC_POSITIONSPECDEF,
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=359,
  serialized_end=465,
)


_MODEMCMD = _descriptor.Descriptor(
  name='ModemCmd',
  full_name='ModemCmd',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='command', full_name='ModemCmd.command', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=467,
  serialized_end=494,
)


_MODEMSTATUS = _descriptor.Descriptor(
  name='ModemStatus',
  full_name='ModemStatus',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='model', full_name='ModemStatus.model', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='IMEI', full_name='ModemStatus.IMEI', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='gps_on', full_name='ModemStatus.gps_on', index=2,
      number=3, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='SIM_status', full_name='ModemStatus.SIM_status', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='IMSI', full_name='ModemStatus.IMSI', index=4,
      number=5, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='registered', full_name='ModemStatus.registered', index=5,
      number=6, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='network_reg', full_name='ModemStatus.network_reg', index=6,
      number=7, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='PLMNID', full_name='ModemStatus.PLMNID', index=7,
      number=8, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='network_name', full_name='ModemStatus.network_name', index=8,
      number=9, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='network', full_name='ModemStatus.network', index=9,
      number=10, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='lac', full_name='ModemStatus.lac', index=10,
      number=15, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='ci', full_name='ModemStatus.ci', index=11,
      number=16, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='rat', full_name='ModemStatus.rat', index=12,
      number=11, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='band', full_name='ModemStatus.band', index=13,
      number=12, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='rssi', full_name='ModemStatus.rssi', index=14,
      number=13, type=17, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='operators', full_name='ModemStatus.operators', index=15,
      number=14, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=497,
  serialized_end=770,
)


_MODEMRESP = _descriptor.Descriptor(
  name='ModemResp',
  full_name='ModemResp',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='frameID', full_name='ModemResp.frameID', index=0,
      number=1, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='response', full_name='ModemResp.response', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='status', full_name='ModemResp.status', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=772,
  serialized_end=848,
)

_POSITIONSPEC.fields_by_name['spec'].enum_type = _POSITIONSPEC_POSITIONSPECDEF
_POSITIONSPEC_POSITIONSPECDEF.containing_type = _POSITIONSPEC
_MODEMRESP.fields_by_name['status'].message_type = _MODEMSTATUS
DESCRIPTOR.message_types_by_name['GPS_Position'] = _GPS_POSITION
DESCRIPTOR.message_types_by_name['GPS_Vector'] = _GPS_VECTOR
DESCRIPTOR.message_types_by_name['GPS_Precision'] = _GPS_PRECISION
DESCRIPTOR.message_types_by_name['PositionSpec'] = _POSITIONSPEC
DESCRIPTOR.message_types_by_name['ModemCmd'] = _MODEMCMD
DESCRIPTOR.message_types_by_name['ModemStatus'] = _MODEMSTATUS
DESCRIPTOR.message_types_by_name['ModemResp'] = _MODEMRESP
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

GPS_Position = _reflection.GeneratedProtocolMessageType('GPS_Position', (_message.Message,), dict(
  DESCRIPTOR = _GPS_POSITION,
  __module__ = 'GPS_Service_pb2'
  # @@protoc_insertion_point(class_scope:GPS_Position)
  ))
_sym_db.RegisterMessage(GPS_Position)

GPS_Vector = _reflection.GeneratedProtocolMessageType('GPS_Vector', (_message.Message,), dict(
  DESCRIPTOR = _GPS_VECTOR,
  __module__ = 'GPS_Service_pb2'
  # @@protoc_insertion_point(class_scope:GPS_Vector)
  ))
_sym_db.RegisterMessage(GPS_Vector)

GPS_Precision = _reflection.GeneratedProtocolMessageType('GPS_Precision', (_message.Message,), dict(
  DESCRIPTOR = _GPS_PRECISION,
  __module__ = 'GPS_Service_pb2'
  # @@protoc_insertion_point(class_scope:GPS_Precision)
  ))
_sym_db.RegisterMessage(GPS_Precision)

PositionSpec = _reflection.GeneratedProtocolMessageType('PositionSpec', (_message.Message,), dict(
  DESCRIPTOR = _POSITIONSPEC,
  __module__ = 'GPS_Service_pb2'
  # @@protoc_insertion_point(class_scope:PositionSpec)
  ))
_sym_db.RegisterMessage(PositionSpec)

ModemCmd = _reflection.GeneratedProtocolMessageType('ModemCmd', (_message.Message,), dict(
  DESCRIPTOR = _MODEMCMD,
  __module__ = 'GPS_Service_pb2'
  # @@protoc_insertion_point(class_scope:ModemCmd)
  ))
_sym_db.RegisterMessage(ModemCmd)

ModemStatus = _reflection.GeneratedProtocolMessageType('ModemStatus', (_message.Message,), dict(
  DESCRIPTOR = _MODEMSTATUS,
  __module__ = 'GPS_Service_pb2'
  # @@protoc_insertion_point(class_scope:ModemStatus)
  ))
_sym_db.RegisterMessage(ModemStatus)

ModemResp = _reflection.GeneratedProtocolMessageType('ModemResp', (_message.Message,), dict(
  DESCRIPTOR = _MODEMRESP,
  __module__ = 'GPS_Service_pb2'
  # @@protoc_insertion_point(class_scope:ModemResp)
  ))
_sym_db.RegisterMessage(ModemResp)



_GPS_SERVICE = _descriptor.ServiceDescriptor(
  name='GPS_Service',
  full_name='GPS_Service',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  serialized_start=851,
  serialized_end=1044,
  methods=[
  _descriptor.MethodDescriptor(
    name='getPosition',
    full_name='GPS_Service.getPosition',
    index=0,
    containing_service=None,
    input_type=_POSITIONSPEC,
    output_type=_GPS_POSITION,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='getVector',
    full_name='GPS_Service.getVector',
    index=1,
    containing_service=None,
    input_type=_POSITIONSPEC,
    output_type=_GPS_VECTOR,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='getPrecision',
    full_name='GPS_Service.getPrecision',
    index=2,
    containing_service=None,
    input_type=_POSITIONSPEC,
    output_type=_GPS_PRECISION,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='modemCommand',
    full_name='GPS_Service.modemCommand',
    index=3,
    containing_service=None,
    input_type=_MODEMCMD,
    output_type=_MODEMRESP,
    serialized_options=None,
  ),
])
_sym_db.RegisterServiceDescriptor(_GPS_SERVICE)

DESCRIPTOR.services_by_name['GPS_Service'] = _GPS_SERVICE

# @@protoc_insertion_point(module_scope)
