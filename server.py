from concurrent import futures
import time
import grpc
import logging
import sys

from lib.main import create_task, get_all_tasks, get_task, update_task, \
    delete_task

from generated_code import todo_pb2_grpc

# logging config
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


class Tasker(todo_pb2_grpc.TaskerServicer):
    def CreateTask(self, request, context):
        logging.info("CreateTask method started")
        logging.info("Received message: {}".format(request))
        return create_task(request)

    def GetAllTasks(self, request, context):
        logging.info("Listing all tasks")
        return get_all_tasks()

    def GetTask(self, request, context):
        return get_task(request)

    def UpdateTask(self, request, context):
        logging.info("Received message: {}".format(request))
        return update_task(request)

    def DeleteTask(self, request, context):
        logging.info("Delete task with ID: {}".format(request.id))
        return delete_task(request)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    todo_pb2_grpc.add_TaskerServicer_to_server(Tasker(), server)
    logging.info("Starting server. Listening on port 50051.")
    server.add_insecure_port('[::]:50051')
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    serve()
