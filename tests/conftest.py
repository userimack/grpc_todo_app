from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import pytest

from database import models

#  from generated_code import todo_pb2
#  from lib.main import create_task


@pytest.fixture(scope='session')
def engine():
    connection_string = 'sqlite:///test_database_todo_app.db'
    engine = create_engine(connection_string)
    return engine


@pytest.yield_fixture(scope='session')
def tables(engine):
    models.Base.metadata.create_all(engine)
    yield
    models.Base.metadata.drop_all(engine)


@pytest.yield_fixture
def db_session(engine, tables):
    #  import ipdb; ipdb.set_trace()
    """Returns an sqlalchemy session, and after the test tears down everything properly."""
    connection = engine.connect()
    # begin the nested transaction
    transaction = connection.begin()
    # use the connection with the already started transaction

    @contextmanager
    def session_scope():
        session = Session(bind=connection)
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    yield session_scope

    # roll back the broader transaction
    transaction.rollback()
    # put back the connection to the connection pool
    connection.close()


@pytest.fixture()
def mock_session(mocker, db_session):
    mocker.patch('lib.main.session_scope', db_session)


#  @pytest.fixture
#  def new_task(mocker, mock_session):
#      task = todo_pb2.Task(description="Task created for testing.")
#      return create_task(task)
#
