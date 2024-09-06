from contextlib import asynccontextmanager
from fastapi_limiter import FastAPILimiter
import redis.asyncio as aioredis
from fastapi import FastAPI
import uvicorn

from src.conf.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    r = aioredis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True
    )
    await FastAPILimiter.init(r)
    yield
    await FastAPILimiter.close()


app = FastAPI(lifespan=lifespan)


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
