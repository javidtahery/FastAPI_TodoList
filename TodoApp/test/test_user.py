from starlette import status

from .utils import *
from ..Roaters.users import get_db, get_current_user



app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_return_user(test_user):
    response = client.get("/user/")
    assert response.status_code == 200
    print(response.json())
    assert response.json()['username'] == 'codingwithroby'
    assert response.json()['first_name'] == 'javid'
    assert response.json()['last_name'] == 'taheri'
    assert response.json()['email'] == 'aaa@gmail.com'
    assert response.json()['phone_number'] == '11111'


def test_change_password_success(test_user):
    response = client.put("/user/password", json={'old_password': '123', 'new_password': '123456'})
    assert response.status_code == 204


def test_change_invalid_password_success(test_user):
    response = client.put("/user/password", json={'old_password': '1234', 'new_password': '123456'})
    assert response.status_code == 401
    assert response.json() == {'detail': 'password is wrong'}


def test_change_phone_number_success(test_user):
    response = client.put("/user/phonenumber/22222")
    assert response.status_code == 204
    db = TestingSessionLocal()
    model = db.query(Users).filter(Users.id == 1).first()
    assert model.phone_number == '22222'


