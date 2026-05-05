from sqlalchemy import StaticPool, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
import pytest
from ..database import Base
from ..main import app
from ..models import Todos, Users
from ..Roaters.auth import bcrypt_context



SQLALCHEMY_DATABASE_URL = "sqlite:///./testdb.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL,
                       connect_args={"check_same_thread": False},
                       poolclass=StaticPool)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_current_user():
    return {'username': 'codingwithroby', 'id': 1, 'user_role': 'admin'}

client = TestClient(app)





@pytest.fixture
def test_todo():
    todo = Todos(
        title="learn",
        description="deep",
        priority=1,
        complete=False,
        owner_id=1,
        id=1
    )

    db = TestingSessionLocal()
    db.add(todo)
    db.commit()
    yield
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos;"))
        connection.commit()


@pytest.fixture()
def test_user():
    user = Users(
        username= 'codingwithroby',
        id= 1,
        role= 'admin',
        first_name="javid",
        last_name="taheri",
        email="aaa@gmail.com",
        hash_password=bcrypt_context.hash("123"),
        phone_number="11111"
    )
    db = TestingSessionLocal()
    db.add(user)
    db.commit()
    yield user
    with engine.connect() as c:
        c.execute(text("delete from userss;"))
        c.commit()












