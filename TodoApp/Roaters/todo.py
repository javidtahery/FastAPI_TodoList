from typing import Annotated

from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Path, HTTPException, Body, Request
from starlette import status
from ..models import Todos
from ..database import engine, SessionLocal
from . import auth
from .auth import get_current_user
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates


templates = Jinja2Templates(directory="TodoApp/templates")

router = APIRouter(
    prefix="/todos",
    tags=["Todos"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class TODO_OBJ (BaseModel):
    title: str
    description: str
    priority: int
    complete: bool


def redirect_to_login():
    redirect_response = RedirectResponse(url="/auth/login-page", status_code=status.HTTP_302_FOUND)
    redirect_response.delete_cookie(key="access_token")
    return redirect_response


### PAges ###
@router.get("/todo-page")
async def render_todo_page(request: Request, db: db_dependency):
    print("render_todo_page !!!")
    try:
        user = await get_current_user(request.cookies.get('access_token'))

        if user is None:
            print("user not found")
            return redirect_to_login()
        todos = db.query(Todos).filter(Todos.owner_id == user.get('id')).all()
        return templates.TemplateResponse(request=request, name="todo.html", context={"todos": todos, "user": user})
        # return templates.TemplateResponse({"request" : request , "todos": todos, "user": user}, name="todo.html")
    except:
        return redirect_to_login()


@router.get("/add-todo-page")
async def render_todo_page(request: Request):
    try:
        user = await get_current_user(request.cookies.get('access_token'))
        if user is None:
            return redirect_to_login()

        return templates.TemplateResponse(request=request, name="add-todo.html", context={"user": user})
    except:
        return redirect_to_login()

@router.get("/edit-todo-page/{todo_id}")
async def render_edit_todo(request: Request, todo_id: int, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get("access_token"))

        if user is None:
            return redirect_to_login()

        todo = db.query(Todos).filter(Todos.id == todo_id).first()
        return templates.TemplateResponse(request=request, name="edit-todo.html", context={"todo": todo, "user": user})
    except:
        print("exception: edit-todo-page")
        return redirect_to_login()

### end-points ###
@router.get("/", status_code=status.HTTP_200_OK)
async def read_all_db(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="user is not available")
    return db.query(Todos).filter(Todos.owner_id == user.get('id')).all()


@router.post("/new_todo", status_code=status.HTTP_201_CREATED)
async def add_todo(user: user_dependency, db: db_dependency, new_item: TODO_OBJ):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="user is not available")
    db_model = Todos(**new_item.model_dump(), owner_id=user.get('id'))
    db.add(db_model)
    db.commit()


@router.get("/{id_code}", status_code=status.HTTP_200_OK)
async def read_specific_TODO(user: user_dependency, db: db_dependency, id_code: int = Path(gt= 0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="user is not available")
    my_todo = db.query(Todos).filter(Todos.id == id_code).filter(Todos.owner_id == user.get('id')).first()
    if my_todo is not None :
        return my_todo
    else:
        raise HTTPException(status_code=404, detail='todo not found')


@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency, db: db_dependency, todo_request: TODO_OBJ, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="user is not available")

    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).first()
    if todo_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='not found')
    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete
    db.add(todo_model)
    db.commit()


@router.delete("/todo/{todo_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="user is not available")
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).first()
    if todo_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found")
    else:
        db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).delete()
        db.commit()