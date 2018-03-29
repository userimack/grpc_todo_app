import traceback
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Database connection string
engine = create_engine("sqlite:///database_todo_app.db", echo=False)
#  conn = engine.connect()
Session = sessionmaker(bind=engine)


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

