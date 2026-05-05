from starlette import status

from .utils import *
from ..Roaters.admin import get_db, get_current_user
from ..models import Todos



app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_admin_read_all_authenticated(test_todo):
    response = client.get("admin/todo")
    assert response.status_code == 200
    assert response.json() == [{'complete': False, 'id': 1, 'priority': 1, 'title': 'learn', 'description': 'deep',
                                'owner_id': 1}]


def test_delete_admin(test_todo):
    response = client.delete("/admin/todo/1")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db2 = TestingSessionLocal()
    model = db2.query(Todos).filter(Todos.id == 1).first()
    assert model is None

def test_delete_not_found_admin(test_todo):
    response = client.delete("/admin/todo/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'not found'}