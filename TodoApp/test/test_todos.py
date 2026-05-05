

from fastapi import status

from ..models import Todos

from ..Roaters.todo import get_db, get_current_user
from .utils import *



app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user



'''GET'''

def test_read_all_authenticated(test_todo):
    response = client.get("/todos/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'complete': False, 'id': 1, 'priority': 1, 'title': 'learn', 'description': 'deep',
                                'owner_id': 1}]


def test_read_one_authenticated(test_todo):
    response = client.get("/todos/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'complete': False, 'id': 1, 'priority': 1, 'title': 'learn', 'description': 'deep',
                                'owner_id': 1}

def test_read_one_authenticated_not_found(test_todo):
    response = client.get("/todos/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'todo not found'}

'''Post'''
def test_create_todo(test_todo):
    request_data={
        'title': 'new todo1',
        'description': 'new todo description',
        'priority': 5,
        'complete': False
    }
    response = client.post("/todos/new_todo", json=request_data)
    assert response.status_code == 201
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 2).first()
    assert model.title == request_data.get('title')
    assert model.description == request_data.get('description')
    assert model.priority == request_data.get('priority')
    assert model.complete == request_data.get('complete')

def test_update_todo(test_todo):
    request_data={'complete': True, 'id': 1, 'priority': 1, 'title': 'learn', 'description': 'deep',
                                'owner_id': 1}

    response = client.put("/todos/todo/1", json=request_data)
    assert response.status_code == 204
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert request_data.get('complete') == model.complete


def test_update_not_found_todo(test_todo):
    request_data={'complete': True, 'id': 1, 'priority': 1, 'title': 'learn', 'description': 'deep',
                                'owner_id': 1}

    response = client.put("/todos/todo/9999", json=request_data)
    assert response.status_code == 404
    assert response.json() == {'detail': 'not found'}


def test_delete_todo(test_todo):
    response = client.delete("/todos/todo/1")
    assert response.status_code == 204
    # assert response.json() == []
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model is None

def test_delete_notfound_todo(test_todo):
    response = client.delete("/todos/todo/15674")
    assert response.status_code == 404
    assert response.json() == {'detail': 'not found'}
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model is not None