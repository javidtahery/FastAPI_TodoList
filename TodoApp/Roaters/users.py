from typing import Annotated

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Path, HTTPException, Body
from starlette import status
from ..models import Todos, Users
from ..database import engine, SessionLocal
from . import auth
from .auth import get_current_user
from passlib.context import CryptContext

router = APIRouter(
    prefix="/user",
    tags=["user"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class UserVerification(BaseModel):
    old_password: str
    new_password: str = Field(min_length=6)


@router.get("/", status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='user is not valied')
    return db.query(Users).filter(Users.id == user.get('id')).first()


@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def get_user(user: user_dependency, db: db_dependency, userPass: UserVerification):
    if user is None:
        raise HTTPException(status_code=401, detail='user is not valied')
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    if bcrypt_context.verify(userPass.old_password, user_model.hash_password):
        # put hashed password to database
        new_pass_hashed = bcrypt_context.hash(userPass.new_password)
        user_model.hash_password = new_pass_hashed
        db.add(user_model)
        db.commit()
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='password is wrong')


@router.put("/phonenumber/{pnumber}", status_code=status.HTTP_204_NO_CONTENT)
async def change_phone_number(user: user_dependency, db: db_dependency, pnumber: str):
    if user is None:
        raise HTTPException(status_code=401, detail="user not available")
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    user_model.phone_number = pnumber
    db.add(user_model)
    db.commit()
