from concurrent import futures
import time
import grpc
import logging
import sys

#  import traceback

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from generated_code import todo_pb2
from generated_code import todo_pb2_grpc

from database.models import Task

# logging config
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

# Database connection string
engine = create_engine("sqlite:///database_todo_app.db", echo=True)
#  conn = engine.connect()
Session = sessionmaker(bind=engine)

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

DATA_STORE = {}


class Tasker(todo_pb2_grpc.TaskerServicer):
    def CreateTask(self, request, context):
        logging.info("CreateTask method started")
        logging.info("Received message: {}".format(request))

        try:
            session = Session()

            task = Task(description=request.description, status=todo_pb2.Task.TaskStatus.Name(request.status))
            session.add(task)
            #  task_id = task.id
            session.commit()

            task_object = session.query(Task).filter_by(id=task.id).first()
            task = todo_pb2.Task(id=task_object.id, description=task_object.description, status=todo_pb2.Task.TaskStatus.Value(task_object.status))

            task_status = todo_pb2.OperationStatus(status=1)

        except Exception as e:
            session.rollback()
            logging.error(e)

            #  print(traceback.format_exc())

            task = todo_pb2.Task()
            task_status = todo_pb2.OperationStatus(status=2)
        finally:
            session.close()

        logging.info("CreateTask method completed")

        return todo_pb2.CreateTaskResponse(op_status=task_status, task=task)

    def GetAllTasks(self, request, context):
        logging.info("Listing all tasks")
        session = Session()

        result_list = []

        for task_object in session.query(Task).all():
            #  import ipdb; ipdb.set_trace();
            task = todo_pb2.Task(id=task_object.id, description=task_object.description, status=todo_pb2.Task.TaskStatus.Value(task_object.status))
            print("--->")
            logging.info(task)
            print("--->")
            result_list.extend([task])

        logging.info(result_list)
        session.close()

        return todo_pb2.TasksList(tasks=result_list)

    def GetTask(self, request, context):
        try:
            session = Session()
            logging.info("Received ID: {}".format(request))
            #  task = DATA_STORE.get(request.id, todo_pb2.Task())
            task_object = session.query(Task).filter_by(id=request.id).one()
            task = todo_pb2.Task(id=task_object.id, description=task_object.description, status=todo_pb2.Task.TaskStatus.Value(task_object.status))
            logging.info("Got data: {}".format(task))
        except Exception as e:
            task = todo_pb2.Task()
            logging.error(e)

        finally:
            session.close()

        return task

    def UpdateTask(self, request, context):
        logging.info("Received message: {}".format(request))

        try:
            session = Session()
            task_object = session.query(Task).filter_by(id=request.id).update({Task.status: todo_pb2.Task.TaskStatus.Name(request.status)})
            session.commit()

            task_object = session.query(Task).filter_by(id=request.id).one()

            task = todo_pb2.Task(id=task_object.id, description=task_object.description, status=todo_pb2.Task.TaskStatus.Value(task_object.status))

            task_status = todo_pb2.OperationStatus(status=1)

            return todo_pb2.CreateTaskResponse(op_status=task_status, task=task)
        except Exception as e:
            session.rollback()
            logging.error(e)

            task = todo_pb2.Task()
            task_status = todo_pb2.OperationStatus(status=2)
            return todo_pb2.CreateTaskResponse(op_status=task_status, task=task)
        finally:
            session.close()

    def DeleteTask(self, request, context):
        logging.info("Delete task with ID: {}".format(request.id))

        try:
            session = Session()
            task = session.query(Task).filter_by(id=request.id).one()
            session.delete(task)
            session.commit()

            task_status = todo_pb2.OperationStatus(status=1)

            return todo_pb2.DeleteTaskResponse(op_status=task_status)
        except Exception as e:
            session.rollback()
            logging.error(e)
            task_status = todo_pb2.OperationStatus(status=2)

        finally:
            session.close()

            return todo_pb2.DeleteTaskResponse(op_status=task_status)


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
