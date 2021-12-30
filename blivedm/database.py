from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

base = declarative_base()

class Message(base):
    __tablename__ = "message"

    id = Column(Integer, primary_key=True)
    uid = Column(Integer)
    rid = Column(Integer)
    uname = Column(String(255))
    msg = Column(String(1024))
    time = Column(DateTime)
    privilege_type = Column(Integer)
