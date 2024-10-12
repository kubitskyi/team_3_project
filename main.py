"""PixnTalk API Application

This module defines the FastAPI application for the PixnTalk platform. It includes
route configurations for authentication, users, posts, and comments, as well as
integration with Redis for rate limiting and other functionalities.

The application lifecycle is managed using an asynchronous context manager to handle
resource initialization and cleanup, including setting up and closing the Redis connection.

Dependencies:
- FastAPI: The web framework for building APIs.
- redis.asyncio: Asynchronous Redis client for managing data in Redis.
- fastapi_limiter: Rate limiting middleware to control API access.

Application Routes:
- Authentication routes
- User management routes
- Post management routes
- Comment management routes

Health Check:
- A health check endpoint is provided to verify that the API is running.

Usage:
To run the application, execute the module directly, and it will start a server
on localhost at port 8000.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
import uvicorn
import redis.asyncio as redis
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

from src.conf.config import settings
from src.routes import auth
from src.routes import users
from src.routes import posts
from src.routes import comments


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
        db=0,
        encoding="utf-8",
        decode_responses=True
    )
    await FastAPILimiter.init(r)
    app.state.redis = r
    yield
    await r.close()


app = FastAPI(title="PixnTalk", lifespan=lifespan)

app.include_router(auth.router, prefix='/api')
app.include_router(users.router, prefix='/api')
app.include_router(posts.router, prefix='/api')
app.include_router(comments.router, prefix='/api')


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
