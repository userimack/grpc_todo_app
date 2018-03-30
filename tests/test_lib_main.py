#  import pytest

from lib.main import create_task, get_all_tasks, get_task, update_task, \
    delete_task

#  from database.connection import session_scope
from generated_code import todo_pb2

#  from database.models import Task


#  @pytest.fixture()
#  def setup():
#      task = todo_pb2.Task(description="Task created for testing.")
#      return task


def test_create_task(mock_session):
    task = todo_pb2.Task(description="Task created for testing.")
    response = create_task(task)
    print(type(response.task.status))

    assert response.task.description == task.description
    assert isinstance(response, todo_pb2.CreateTaskResponse)
    assert response.task.id is not None
    assert type(response.task.id) is int
    assert response.task.status is not None
    assert type(response.task.status) is int


def test_create_task_with_empty_description(mock_session):
    task = todo_pb2.Task()
    response = create_task(task)

    assert response.op_status.status == todo_pb2.OperationStatus.FAILED


def test_get_task(mock_session):
    task = todo_pb2.Task(description="Task created for testing.")
    response_create_task = create_task(task)
    response_get_task = get_task(todo_pb2.Task(id=response_create_task.task.id))

    assert response_create_task.task.description == response_get_task.description


def test_get_task_with_improper_request(mock_session):
    response_get_task = get_task(todo_pb2.Task())
    assert isinstance(response_get_task, todo_pb2.Task)


def test_get_all_tasks(mock_session):
    response = get_all_tasks()

    assert isinstance(response, todo_pb2.TasksList)


def test_update_task(mock_session):
    task = todo_pb2.Task(description="Task created for testing.")
    response_create_task = create_task(task)
    response_update_task = update_task(todo_pb2.Task(id=response_create_task.task.id, status=todo_pb2.Task.INPROGRESS))

    assert response_create_task.task.status != response_update_task.task.status


def test_update_task_with_improper_request(mock_session):
    response_update_task = delete_task(todo_pb2.Task())
    assert response_update_task.op_status.status == todo_pb2.OperationStatus.FAILED


def test_delete_task(mock_session):
    task = todo_pb2.Task(description="Task created for testing.")
    response_create_task = create_task(task)
    response_delete_task = delete_task(todo_pb2.Task(id=response_create_task.task.id))

    assert response_delete_task.op_status.status == todo_pb2.OperationStatus.SUCCESS


def test_delete_task_with_improper_request(mock_session):
    response_delete_task = delete_task(todo_pb2.Task())
    assert response_delete_task.op_status.status == todo_pb2.OperationStatus.FAILED
