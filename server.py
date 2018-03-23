from concurrent import futures
import time

import grpc

from generated_code import todo_pb2
from generated_code import todo_pb2_grpc

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

DATA_STORE = {}


class Tasker(todo_pb2_grpc.TaskerServicer):
    def CreateTask(self, request, context):
        print("Received message: %s" % request)

        task = todo_pb2.Task()
        task.id = request.id
        task.description = request.description
        task.status = request.status

        DATA_STORE[request.id] = task
        dummy_status = todo_pb2.OperationStatus(status=1)

        return todo_pb2.CreateTaskResponse(op_status=dummy_status)

    def GetAllTasks(self, request, context):
        print("Listing all tasks")
        return todo_pb2.TasksList(tasks=DATA_STORE.values())

    def GetTask(self, request, context):
        print("Received message: %s" % request)
        task = DATA_STORE.get(request.id, None)
        print("Got data", task)
        #  import pdb;pdb.set_trace()
        if task is not None:
            print("Returning ", task)
            return task  # todo_pb2.Task(id=task.id, description=task.description, status=task.status)
        else:
            return todo_pb2.Task()

    def DeleteTask(self, request, context):
        task = DATA_STORE.pop(request.id, None)

        success_status = todo_pb2.OperationStatus(status=1)
        failed_status = todo_pb2.OperationStatus(status=2)
        if task is not None:

            return todo_pb2.DeleteTaskResponse(op_status=success_status)
        else:
            return todo_pb2.DeleteTaskResponse(op_status=failed_status)
            #  return "Error: Task with id: {} is not found".format(request.id)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    todo_pb2_grpc.add_TaskerServicer_to_server(Tasker(), server)
    print("Starting server. Listening on port 50051.")
    server.add_insecure_port('[::]:50051')
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    serve()
