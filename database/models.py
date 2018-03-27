from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Sequence

Base = declarative_base()


class Task(Base):
    __tablename__ = 'task'
    id = Column(Integer, Sequence('task_id_seq'), primary_key=True)
    description = Column(String(200))
    status = Column(String(100))

    def __repr__(self):
        return "<Task(id='{}', description='{}', status='{}')>".format(
            self.id, self.description, self.status)

