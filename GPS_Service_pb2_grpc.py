# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

import GPS_Service_pb2 as GPS__Service__pb2


class GPS_ServiceStub(object):
  # missing associated documentation comment in .proto file
  pass

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.getPosition = channel.unary_unary(
        '/GPS_Service/getPosition',
        request_serializer=GPS__Service__pb2.PositionSpec.SerializeToString,
        response_deserializer=GPS__Service__pb2.GPS_Position.FromString,
        )
    self.getVector = channel.unary_unary(
        '/GPS_Service/getVector',
        request_serializer=GPS__Service__pb2.PositionSpec.SerializeToString,
        response_deserializer=GPS__Service__pb2.GPS_Vector.FromString,
        )
    self.getPrecision = channel.unary_unary(
        '/GPS_Service/getPrecision',
        request_serializer=GPS__Service__pb2.PositionSpec.SerializeToString,
        response_deserializer=GPS__Service__pb2.GPS_Precision.FromString,
        )
    self.streamGPS = channel.unary_stream(
        '/GPS_Service/streamGPS',
        request_serializer=GPS__Service__pb2.ModemCmd.SerializeToString,
        response_deserializer=GPS__Service__pb2.GPS_Vector.FromString,
        )
    self.stopStream = channel.unary_unary(
        '/GPS_Service/stopStream',
        request_serializer=GPS__Service__pb2.ModemCmd.SerializeToString,
        response_deserializer=GPS__Service__pb2.ModemResp.FromString,
        )
    self.modemCommand = channel.unary_unary(
        '/GPS_Service/modemCommand',
        request_serializer=GPS__Service__pb2.ModemCmd.SerializeToString,
        response_deserializer=GPS__Service__pb2.ModemResp.FromString,
        )
    self.sendSMS = channel.unary_unary(
        '/GPS_Service/sendSMS',
        request_serializer=GPS__Service__pb2.SMS.SerializeToString,
        response_deserializer=GPS__Service__pb2.ModemResp.FromString,
        )
    self.checkSMSCommand = channel.unary_unary(
        '/GPS_Service/checkSMSCommand',
        request_serializer=GPS__Service__pb2.checkSMS.SerializeToString,
        response_deserializer=GPS__Service__pb2.receivedSMSList.FromString,
        )


class GPS_ServiceServicer(object):
  # missing associated documentation comment in .proto file
  pass

  def getPosition(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def getVector(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def getPrecision(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def streamGPS(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def stopStream(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def modemCommand(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def sendSMS(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def checkSMSCommand(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_GPS_ServiceServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'getPosition': grpc.unary_unary_rpc_method_handler(
          servicer.getPosition,
          request_deserializer=GPS__Service__pb2.PositionSpec.FromString,
          response_serializer=GPS__Service__pb2.GPS_Position.SerializeToString,
      ),
      'getVector': grpc.unary_unary_rpc_method_handler(
          servicer.getVector,
          request_deserializer=GPS__Service__pb2.PositionSpec.FromString,
          response_serializer=GPS__Service__pb2.GPS_Vector.SerializeToString,
      ),
      'getPrecision': grpc.unary_unary_rpc_method_handler(
          servicer.getPrecision,
          request_deserializer=GPS__Service__pb2.PositionSpec.FromString,
          response_serializer=GPS__Service__pb2.GPS_Precision.SerializeToString,
      ),
      'streamGPS': grpc.unary_stream_rpc_method_handler(
          servicer.streamGPS,
          request_deserializer=GPS__Service__pb2.ModemCmd.FromString,
          response_serializer=GPS__Service__pb2.GPS_Vector.SerializeToString,
      ),
      'stopStream': grpc.unary_unary_rpc_method_handler(
          servicer.stopStream,
          request_deserializer=GPS__Service__pb2.ModemCmd.FromString,
          response_serializer=GPS__Service__pb2.ModemResp.SerializeToString,
      ),
      'modemCommand': grpc.unary_unary_rpc_method_handler(
          servicer.modemCommand,
          request_deserializer=GPS__Service__pb2.ModemCmd.FromString,
          response_serializer=GPS__Service__pb2.ModemResp.SerializeToString,
      ),
      'sendSMS': grpc.unary_unary_rpc_method_handler(
          servicer.sendSMS,
          request_deserializer=GPS__Service__pb2.SMS.FromString,
          response_serializer=GPS__Service__pb2.ModemResp.SerializeToString,
      ),
      'checkSMSCommand': grpc.unary_unary_rpc_method_handler(
          servicer.checkSMSCommand,
          request_deserializer=GPS__Service__pb2.checkSMS.FromString,
          response_serializer=GPS__Service__pb2.receivedSMSList.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'GPS_Service', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))
