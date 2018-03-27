import grpc
import time

from generated_code import todo_pb2
from generated_code import todo_pb2_grpc


channel = grpc.insecure_channel("localhost:50051")

stub = todo_pb2_grpc.TaskerStub(channel)


task = todo_pb2.Task()

task.id = int(time.strftime('%Y%m%d%H%M%S'))

task.description = input("Enter task description: ")

task_status_map = {'complete': todo_pb2.Task.COMPLETE,
                   'progress': todo_pb2.Task.PROGRESS,
                   'todo': todo_pb2.Task.TODO}

task.status = task_status_map.get(input("Enter task status (options: complete, progress, todo or leave blank to fill later): "), todo_pb2.Task.UNKNOWN_TASK_STATUS)

# getAllTaskList
resp = stub.GetAllTasks(todo_pb2.GetAllTasksRequest())
print(resp)

"""
# Working repl code

import grpc
import time

from generated_code import todo_pb2
from generated_code import todo_pb2_grpc


channel = grpc.insecure_channel("localhost:50051")

stub = todo_pb2_grpc.TaskerStub(channel)

task = todo_pb2.Task()
#  task.id = 1 #int(time.strftime('%Y%m%d%H%M%S'))
task.description = "task 1"
task.status = todo_pb2.Task.TODO

task1 = todo_pb2.Task()
#  task1.id = 2 #int(time.strftime('%Y%m%d%H%M%S'))
task1.description = "task 2"
task1.status = todo_pb2.Task.TODO

stub.CreateTask(task)
stub.CreateTask(task1)

print("Listing all tasks")
resp = stub.GetAllTasks(todo_pb2.GetAllTasksRequest())
print(resp)
task2 = todo_pb2.Task(id =3)
task2.id = 1
stub.GetTask(task)
print("Deleting task1")
stub.DeleteTask(task1)
print("Listing all tasks")
resp = stub.GetAllTasks(todo_pb2.GetAllTasksRequest())
print(resp)
"""

