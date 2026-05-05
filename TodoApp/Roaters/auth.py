from datetime import timedelta, datetime, timezone
from typing import Annotated
from sqlalchemy.exc import IntegrityError
from fastapi import APIRouter, Depends, Path, HTTPException, Body, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status
from starlette.status import HTTP_201_CREATED
from passlib.context import CryptContext

from ..database import SessionLocal
from ..models import Users
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError

from fastapi.templating import Jinja2Templates


router = APIRouter( prefix= "/auth", tags=["AUTH"])


#jwt
SECRET_KEY = '1234567890'
ALGORITHM = 'HS256'


bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')


class UserModel(BaseModel):
    username: str
    password: str
    first_name: str
    last_name: str
    email: str
    role: str
    phone_number: str


class Token(BaseModel):
    access_token: str
    token_type: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def athen_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username==username).first()
    if not user :
        return False
    else:
        if not bcrypt_context.verify(password, user.hash_password):
            return False
        else:
            return user


def create_access_token(username: str, user_id: int, role: str, expire_delta: timedelta):
    encode = {'sub': username, 'id': user_id, 'role': role}
    expire = datetime.now(timezone.utc)+expire_delta
    encode.update({'exp': expire})
    print(encode)
    return jwt.encode(encode, key=SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        user_role: str = payload.get('role')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="username is None or user_id is None")
        return {'username': username, 'id': user_id, 'user_role': user_role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="JWTError")


db_dependency = Annotated[Session, Depends(get_db)]


templates = Jinja2Templates(directory="TodoApp/templates")


### Pages ###

@router.get("/login-page")
def render_login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

@router.get("/register-page")
def render_register_page(request: Request):
    return templates.TemplateResponse(request=request, name="register.html")

#############


@router.get("/users")
async def return_all_users(db: db_dependency):
    return db.query(Users).all()


@router.post("/token", response_model=Token)
async def login_to_access_token(form: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = db.query(Users).filter(Users.username == form.username).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='failed to access to user')
    if athen_user(form.username, form.password, db):
        token = create_access_token(user.username, user.id, user.role, timedelta(minutes=20))
        return {'access_token': token, 'token_type': 'bearer'}
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='failed to access to user')


# create user and post on server
@router.post("/")
async def push_user(db: db_dependency, request: UserModel):
    try:
        new_user = Users(
            first_name=request.first_name,
            username=request.username,
            last_name=request.last_name,
            email=request.email,
            hash_password=bcrypt_context.hash(request.password),
            role=request.role,
            phone_number=request.phone_number
        )
        db.add(new_user)
        db.commit()
    except IntegrityError as error:
        db.rollback()  # Always rollback on error to reset the session

        # Get the raw error message from the database driver
        error_msg = str(error.orig)

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )




