from typing import Annotated

from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Path, HTTPException, Body
from starlette import status
from ..models import Todos
from ..database import engine, SessionLocal
from . import auth
from .auth import get_current_user


router = APIRouter(prefix= "/admin", tags=["ADMIN"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/todo", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='authentication failed')
    return db.query(Todos).all()


@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user:user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='authentication failed')
    if db.query(Todos).filter(Todos.id == todo_id).first() is None:
        raise HTTPException(status_code=404, detail='not found')
    else:
        db.query(Todos).filter(Todos.id == todo_id).delete()
        db.commit()

