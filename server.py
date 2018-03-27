from concurrent import futures
import time
import grpc
import logging
import sys

from generated_code import todo_pb2
from generated_code import todo_pb2_grpc

# logging config
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

DATA_STORE = {}


class Tasker(todo_pb2_grpc.TaskerServicer):
    def CreateTask(self, request, context):
        logging.info("CreateTask method started")
        logging.info("Received message: {}".format(request))

        task = todo_pb2.Task()
        task.id = request.id
        task.description = request.description
        task.status = request.status

        DATA_STORE[request.id] = task
        dummy_status = todo_pb2.OperationStatus(status=1)

        logging.info("CreateTask method completed")

        return todo_pb2.CreateTaskResponse(op_status=dummy_status)

    def GetAllTasks(self, request, context):
        logging.info("Listing all tasks")
        response = todo_pb2.TasksList(tasks=DATA_STORE.values())
        logging.info(response)

        return response

    def GetTask(self, request, context):
        logging.info("Received message: {}".format(request))
        task = DATA_STORE.get(request.id, todo_pb2.Task())
        logging.info("Got data: {}".format(task))
        return task

    def DeleteTask(self, request, context):
        logging.info("Delete task with ID: {}".format(request.id))
        task = DATA_STORE.pop(request.id, None)

        success_status = todo_pb2.OperationStatus(status=1)
        failed_status = todo_pb2.OperationStatus(status=2)
        if task is not None:
            return todo_pb2.DeleteTaskResponse(op_status=success_status)
        else:
            return todo_pb2.DeleteTaskResponse(op_status=failed_status)


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
