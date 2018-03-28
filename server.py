from concurrent import futures
import time
import grpc
import logging
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from contextlib import contextmanager

import traceback

from generated_code import todo_pb2
from generated_code import todo_pb2_grpc

from database.models import Task

# logging config
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

# Database connection string
engine = create_engine("sqlite:///database_todo_app.db", echo=False)
#  conn = engine.connect()
Session = sessionmaker(bind=engine)

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        print(traceback.format_exc())
        session.rollback()
        #  logging.error("Some error happend")
        #  logging.error(e)
        raise
    finally:
        session.close()


class Tasker(todo_pb2_grpc.TaskerServicer):
    def create_task_pb(self, task_object):
        task_pb = todo_pb2.Task()

        if task_object is None:
            return task_pb

        if task_object.description is not None:
            task_pb.description = task_object.description

        if task_object.id is not None:
            task_pb.id = task_object.id

        task_pb.status = todo_pb2.Task.TaskStatus.Value(task_object.status)

        #  if task_object.status is None or task_object.status == 'UNKNOWN_TASK_STATUS':
        #      logging.info(">>> status is None setting it to TODO")
        #      task_pb.status = todo_pb2.Task.TODO
        #  else:
        #      logging.info(">>> status is not None")
        #      task_pb.status = todo_pb2.Task.TaskStatus.Value(task_object.status)
        #      logging.info(task_object.status)

        return task_pb

    def create_db_task_object(task_pb):
        pass

    def CreateTask(self, request, context):
        logging.info("CreateTask method started")
        logging.info("Received message: {}".format(request))

        try:
            # Setting up default task status to TODO
            if request.status == 0 or request.status is None:
                request.status = todo_pb2.Task.TODO

            # Raise ValueError if description is not present
            if request.description == "":
                raise ValueError("Description cannot be blank")

            with session_scope() as session:
                task_object = Task(status=todo_pb2.Task.TaskStatus.Name(request.status), description=request.description)
                session.add(task_object)
                session.commit()

            #  with session_scope() as session:
                task_object = session.query(Task).filter_by(id=task_object.id).first()
                logging.info(task_object)
                task_pb = self.create_task_pb(task_object)

                task_status = todo_pb2.OperationStatus(status=1)

        except Exception as e:
            print(traceback.format_exc())
            task_pb = todo_pb2.Task()
            task_status = todo_pb2.OperationStatus(status=2, errors=str(e).split("\n"))

        logging.info("CreateTask method completed")

        return todo_pb2.CreateTaskResponse(op_status=task_status, task=task_pb)

    def GetAllTasks(self, request, context):
        logging.info("Listing all tasks")

        with session_scope() as session:
            tasks_object = session.query(Task).all()

            result_list = list()

            for task_object in tasks_object:
                #  import ipdb; ipdb.set_trace();
                task_pb = self.create_task_pb(task_object)
                result_list.append(task_pb)

        logging.info(result_list)

        return todo_pb2.TasksList(tasks=result_list)

    def GetTask(self, request, context):
        try:
            logging.info("Received ID: {}".format(request))
            with session_scope() as session:
                task_object = session.query(Task).filter_by(id=request.id).one()
                task_pb = self.create_task_pb(task_object)
                logging.info("Got data: {}".format(task_pb))

        except Exception as e:
            task_pb = todo_pb2.Task()
            logging.error(e)

        return task_pb

    def UpdateTask(self, request, context):
        logging.info("Received message: {}".format(request))

        try:
            with session_scope() as session:
                task_object = session.query(Task).filter_by(id=request.id).update({Task.status: todo_pb2.Task.TaskStatus.Name(request.status)})
                session.commit()

                task_object = session.query(Task).filter_by(id=request.id).one()

                task_pb = self.create_task_pb(task_object)
                #  task_pb = todo_pb2.Task(id=task_object.id, description=task_object.description, status=todo_pb2.Task.TaskStatus.Value(task_object.status))

            task_status = todo_pb2.OperationStatus(status=1)

        except Exception as e:
            logging.error(e)
            task_pb = todo_pb2.Task()
            task_status = todo_pb2.OperationStatus(status=2)

        return todo_pb2.CreateTaskResponse(op_status=task_status, task=task_pb)

    def DeleteTask(self, request, context):
        logging.info("Delete task with ID: {}".format(request.id))

        try:
            with session_scope() as session:
                task = session.query(Task).filter_by(id=request.id).one()
                session.delete(task)

                task_status = todo_pb2.OperationStatus(status=1)

        except Exception as e:
            logging.error(e)
            task_status = todo_pb2.OperationStatus(status=2)

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
