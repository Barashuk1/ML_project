from contextlib import asynccontextmanager
from fastapi.responses import HTMLResponse
from fastapi_limiter import FastAPILimiter
import redis.asyncio as aioredis
from fastapi import FastAPI
import uvicorn
import aiofiles

from src.routes import auth, document
from src.conf.config import settings
from src.schemas import *


@asynccontextmanager
async def lifespan(app: FastAPI):
    r = aioredis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
    )
    await FastAPILimiter.init(r)

    yield
    await FastAPILimiter.close()


app = FastAPI(lifespan=lifespan)

origins = ["*"]

app.include_router(auth.router, prefix='/ml_project')
app.include_router(document.router, prefix='/ml_project')


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """
    The read_root function returns the HTML page.
    """
    async with aiofiles.open("src/services/templates/chat.html", mode="r") as file:
        html_content = await file.read()
    return HTMLResponse(content=html_content)


@app.get('/ml_project/register-page', response_class=HTMLResponse)
async def show_register_page():
    async with aiofiles.open("src/services/templates/registration.html", mode="r") as file:
        html_content = await file.read()
    return HTMLResponse(content=html_content)


@app.get('/ml_project/login-page', response_class=HTMLResponse)
async def show_login_page():
    async with aiofiles.open("src/services/templates/login.html", mode="r") as file:
        html_content = await file.read()
        print(html_content)
    return HTMLResponse(content=html_content)


if __name__ == '__main__':
    uvicorn.run(
        app='main:app',
        host='localhost',
        port=8000,
        reload=True,
    )
