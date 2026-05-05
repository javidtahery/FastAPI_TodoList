from .database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey


class Todos(Base):
    __tablename__ = 'todos'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("userss.id"))


class Users(Base):
    __tablename__ = 'userss'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    hash_password= Column(String)
    first_name = Column(String)
    last_name = Column(String)
    IsActive = Column(Boolean, default=True)
    role = Column(String)
    phone_number = Column(String, )
