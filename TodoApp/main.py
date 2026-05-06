from fastapi import FastAPI, Request, status
# from fastapi_offline import FastAPIOffline

from .models import Base
from .database import engine, SessionLocal
from .Roaters import auth
from .Roaters import todo, admin, users
from .AI import AI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.openapi.docs import get_swagger_ui_html


app = FastAPI(docs_url=None, redoc_url=None)


@app.get("/healthy")
def return_healthy_check():
    return {'status': 'healthy'}

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )


Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="TodoApp/static"), name="static")


@app.get("/")
def test(request: Request):
    return RedirectResponse(url="/todos/todo-page", status_code=status.HTTP_302_FOUND)


app.include_router(auth.router)
app.include_router(todo.router)
app.include_router(admin.router)
app.include_router(users.router)
app.include_router(AI.router)

