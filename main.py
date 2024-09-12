from contextlib import asynccontextmanager
from fastapi.responses import HTMLResponse
from fastapi_limiter import FastAPILimiter
from fastapi.middleware.cors import CORSMiddleware
import redis.asyncio as aioredis
from fastapi import FastAPI
import uvicorn
import aiofiles

from src.routes import auth, document
from src.conf.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # r = aioredis.from_url(
    #     settings.redis_docker_url,
    #     encoding="utf-8",
    #     decode_responses=True
    # )
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

@app.get('/', response_class=HTMLResponse)
async def read_root():
    """
    The read_root function returns a dictionary with the key 'message' and
    value 'Welcome to our ML project'.

    :return: A dictionary
    """
    async with aiofiles.open("src/services/templates/chat.html", mode="r") as file:
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
