from contextlib import asynccontextmanager
from fastapi_limiter import FastAPILimiter
from fastapi.middleware.cors import CORSMiddleware
import redis.asyncio as aioredis
from fastapi import FastAPI
import uvicorn

from src.routes import auth
from src.conf.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        r = aioredis.from_url(
            settings.redis_docker_url,
            encoding="utf-8",
            decode_responses=True
        )
        await FastAPILimiter.init(r)
    except Exception:
        r = aioredis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
        )
        await FastAPILimiter.init(r)

    yield
    await FastAPILimiter.close()


app = FastAPI(lifespan=lifespan)

origins = ["*"]

app.include_router(auth.router, prefix='/api')

@app.get('/')
async def read_root():
    """
    The read_root function returns a dictionary with the key 'message' and
    value 'Welcome to our ML project'.

    :return: A dictionary
    """
    return {'message': 'Welcome to our ML project'}


if __name__ == '__main__':
    uvicorn.run(
        app='main:app',
        host='localhost',
        port=8000,
        reload=True,
    )
