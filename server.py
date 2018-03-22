from concurrent import futures
import time

import grpc

import todo_pb2
import todo_pb2_grpc

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


class TaskManager(todo_pb2_grpc.TaskManagerServicer):
    def Task(self, request, context):
        pass


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    #  hellostreamingworld_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    serve()
