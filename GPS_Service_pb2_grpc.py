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
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'GPS_Service', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))
