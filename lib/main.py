import logging
import sys
import traceback

from database.connection import session_scope
from generated_code import todo_pb2

from database.models import Task

# logging config
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


def create_task_pb(task_object):
    task_pb = todo_pb2.Task()

    if task_object is None:
        return task_pb

    if task_object.description is not None:
        task_pb.description = task_object.description

    if task_object.id is not None:
        task_pb.id = task_object.id

    task_pb.status = todo_pb2.Task.TaskStatus.Value(task_object.status)

    return task_pb


def create_db_task_object(task_pb):
    pass


def create_task(request):
    try:
        # Setting up default task status to TODO
        if request.status == 0 or request.status is None:
            request.status = todo_pb2.Task.TODO

        # Raise ValueError if description is not present
        if request.description == "":
            raise ValueError("Description cannot be blank")

        with session_scope() as session:
            task_object = Task(status=todo_pb2.Task.TaskStatus.Name(request.status),
                               description=request.description)
            session.add(task_object)
            session.commit()

            task_object = session.query(Task).filter_by(
                id=task_object.id).first()
            logging.info(task_object)
            task_pb = create_task_pb(task_object)

            task_status = todo_pb2.OperationStatus(status=1)
    except Exception as e:
        print(traceback.format_exc())
        task_pb = todo_pb2.Task()
        task_status = todo_pb2.OperationStatus(
            status=2, errors=str(e).split("\n"))

    return todo_pb2.CreateTaskResponse(op_status=task_status, task=task_pb)


def get_all_tasks():
    with session_scope() as session:
        tasks_object = session.query(Task).all()

        result_list = list()

        for task_object in tasks_object:
            #  import ipdb; ipdb.set_trace();
            task_pb = create_task_pb(task_object)
            result_list.append(task_pb)

    logging.info(result_list)
    return todo_pb2.TasksList(tasks=result_list)


def get_task(request):
    logging.info("Received ID: {}".format(request))
    try:
        with session_scope() as session:
            task_object = session.query(Task).filter_by(id=request.id).one()
            task_pb = create_task_pb(task_object)
            logging.info("Got data: {}".format(task_pb))
    except Exception as e:
        task_pb = todo_pb2.Task()
        logging.error(e)

    return task_pb


def update_task(request):
    try:
        with session_scope() as session:
            task_object = session.query(Task).filter_by(id=request.id).update(
                {Task.status: todo_pb2.Task.TaskStatus.Name(request.status)})
            session.commit()

            task_object = session.query(Task).filter_by(id=request.id).one()
            task_pb = create_task_pb(task_object)

        task_status = todo_pb2.OperationStatus(status=1)
    except Exception as e:
        logging.error(e)
        task_pb = todo_pb2.Task()
        task_status = todo_pb2.OperationStatus(status=2)

    return todo_pb2.CreateTaskResponse(op_status=task_status, task=task_pb)


def delete_task(request):
    try:
        with session_scope() as session:
            task = session.query(Task).filter_by(id=request.id).one()
            session.delete(task)

            task_status = todo_pb2.OperationStatus(status=1)
    except Exception as e:
        logging.error(e)
        task_status = todo_pb2.OperationStatus(status=2)

    return todo_pb2.DeleteTaskResponse(op_status=task_status)
