import pytest

from lib.main import create_task, get_all_tasks, get_task, update_task, \
    delete_task, create_task_pb

#  from database.connection import session_scope
from generated_code import todo_pb2

#  from database.models import Task


@pytest.fixture()
def task_with_description():
    return todo_pb2.Task(description="Task created for testing.")


@pytest.fixture()
def task_with_no_description():
    return todo_pb2.Task()


def test_create_task(task_with_description, mock_session):
    response = create_task(task_with_description)
    print(type(response.task.status))

    assert response.task.description == task_with_description.description
    assert isinstance(response, todo_pb2.CreateTaskResponse)
    assert response.task.id is not None
    assert type(response.task.id) is int
    assert response.task.status is not None
    assert type(response.task.status) is int


def test_create_task_with_empty_description(task_with_no_description, mock_session):
    response = create_task(task_with_no_description)
    assert response.op_status.status == todo_pb2.OperationStatus.FAILED


def test_get_task(task_with_description, mock_session):
    response_create_task = create_task(task_with_description)
    response_get_task = get_task(todo_pb2.Task(id=response_create_task.task.id))

    assert response_create_task.task.description == response_get_task.description


def test_get_task_with_improper_request(task_with_no_description, mock_session):
    response_get_task = get_task(task_with_no_description)
    assert isinstance(response_get_task, todo_pb2.Task)


def test_get_all_tasks(mock_session):
    for index in range(2):
        task = todo_pb2.Task(description="Task created for testing - {}.".format(index))
        create_task(task)

    response = get_all_tasks()
    assert isinstance(response, todo_pb2.TasksList)


def test_update_task(task_with_description, mock_session):
    response_create_task = create_task(task_with_description)
    response_update_task = update_task(todo_pb2.Task(
        id=response_create_task.task.id, status=todo_pb2.Task.INPROGRESS))

    assert response_create_task.task.status != response_update_task.task.status


def test_update_task_with_improper_request(task_with_no_description, mock_session):
    response_update_task = update_task(task_with_no_description)
    assert response_update_task.op_status.status == todo_pb2.OperationStatus.FAILED


def test_delete_task(task_with_description, mock_session):
    response_create_task = create_task(task_with_description)
    response_delete_task = delete_task(todo_pb2.Task(id=response_create_task.task.id))

    assert response_delete_task.op_status.status == todo_pb2.OperationStatus.SUCCESS


def test_delete_task_with_improper_request(task_with_no_description, mock_session):
    response_delete_task = delete_task(task_with_no_description)
    assert response_delete_task.op_status.status == todo_pb2.OperationStatus.FAILED


def test_create_task_pb_with_none_task_object():
    task_object = None
    assert isinstance(create_task_pb(task_object), todo_pb2.Task)
