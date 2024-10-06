from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
import uvicorn
import redis.asyncio as redis
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
# pylint: disable=C0103, W0613, W0621, W0603
from src.conf.config import settings
from src.routes import users
from src.routes import posts


r = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Define the lifespan of the FastAPI application.

    This function manages the lifecycle of the FastAPI application, initializing and closing
    resources such as Redis and FastAPILimiter during the app's lifespan.

    Args:
        app (FastAPI): The FastAPI application instance.

    Yields:
        Allows the FastAPI application to run within this context, managing resources.
    """
    global r
    r = await redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=0, encoding="utf-8",
        decode_responses=True
    )
    await FastAPILimiter.init(r)

    yield

    await r.close()


app = FastAPI(title="PixnTalk", lifespan=lifespan)

app.include_router(users.router, prefix='/api')
app.include_router(posts.router, prefix='/api')


@app.get("/", dependencies=[Depends(RateLimiter(times=5, seconds=30))])
def read_root():
    """Healthchecker"""
    return {"message": "PixnTalk API is alive"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="localhost",
        port=8000,
        reload=True
    )
