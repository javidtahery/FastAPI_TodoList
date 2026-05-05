from fastapi import FastAPI, Request, status
from fastapi_offline import FastAPIOffline

from .models import Base
from .database import engine, SessionLocal
from .Roaters import auth
from .Roaters import todo, admin, users
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

# 1. Disable the default docs so they don't conflict
app = FastAPI()

# @app.get("/")
# def return_check():
#     pass

@app.get("/healthy")
def return_healthy_check():
    return {'status': 'healthy'}


# 2. Pass the app as a named argument
FastAPIOffline(app=app)

Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="TodoApp/static"), name="static")


@app.get("/")
def test(request: Request):
    return RedirectResponse(url="/todos/todo-page", status_code=status.HTTP_302_FOUND)


app.include_router(auth.router)
app.include_router(todo.router)
app.include_router(admin.router)
app.include_router(users.router)

