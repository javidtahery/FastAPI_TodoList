from starlette import status

from .utils import *
from ..Roaters.auth import get_db, athen_user, create_access_token, SECRET_KEY, ALGORITHM, get_current_user
from ..models import Todos
from jose import jwt
from datetime import datetime, timedelta
import pytest
from fastapi import HTTPException

app.dependency_overrides[get_db] = override_get_db

def test_athenticate_user(test_user):
    db = TestingSessionLocal()
    athenticated_user = athen_user(test_user.username, '123', db)
    assert athenticated_user is not False and not None
    assert athenticated_user.username == test_user.username

    nonexist_athenticated_user = athen_user('stxhyjcyuvb', '123', db)
    assert nonexist_athenticated_user is False or None

    wrong_pass = athen_user(test_user.username, '1236yd', db)
    assert wrong_pass is False or None


def test_create_access_token():
    username = 'testuser'
    user_id = 1
    role = 'user'
    expire_delta = timedelta(days=1)

    token = create_access_token(username, user_id, role, expire_delta)
    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={'verify_signature': False})

    assert decoded['sub'] == username
    assert decoded['id'] == user_id
    assert decoded['role'] == role


@pytest.mark.asyncio
async def test_get_current_user_valid_token():
    encode = {'sub': 'testuser', 'id': 1, 'role': 'admin'}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
    user = await get_current_user(token=token)
    assert user == {'username': 'testuser', 'id': 1, 'user_role': 'admin'}


@pytest.mark.asyncio
async def test_get_current_user_missing_payload():
    encode = {'role': 'admin'}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(token=token)
    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == 'username is None or user_id is None'




