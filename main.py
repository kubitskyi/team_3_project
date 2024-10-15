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
import redis.asyncio as redis

from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

from src.conf.config import settings
from src.routes import auth, transformations, users, posts, comments

r = None

@asynccontextmanager
async def lifespan(app_: FastAPI):
    """Define the lifespan of the FastAPI application.

    This function manages the lifecycle of the FastAPI application, initializing and closing
    resources such as Redis and FastAPILimiter during the app's lifespan.

    Args:
        app_ (FastAPI): The FastAPI application instance.

    Yields:
        Allows the FastAPI application to run within this context, managing resources.
    """

    global r
    r = await redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        password=settings.redis_password,
        db=0,
        encoding="utf-8",
        decode_responses=True,
        ssl=settings.redis_ssl
    )
    await FastAPILimiter.init(r)
    app_.state.redis = r
    yield
    await r.close()


app = FastAPI(
    title="PixnTalk",
    lifespan=lifespan,
    description="**PixnTalk** is a social networking platform designed to enhance user interaction \
        and engagement through dynamic features.\n\nUsers can create accounts, manage their \
        and participate in discussions via posts and comments. The app allows users to upload \
        profiles, and save profile photos to Cloudinary, ensuring efficient storage and retrieval. \
        \n\nAdditionally, PixnTalk includes a photo rating system, enabling users to rate and \
        appreciate each other's uploads. With robust role-based access controls and a focus on \
        community moderation, PixnTalk fosters a secure and vibrant environment for users to \
        connect and share. \n\nBuilt on FastAPI, the application offers high performance and \
        responsiveness, while Redis is utilized for effective rate limiting and data management."
)

app.include_router(auth.router, prefix='/api')
app.include_router(users.router, prefix='/api')
app.include_router(posts.router, prefix='/api')
app.include_router(comments.router, prefix='/api')
app.include_router(transformations.router, prefix='/api')


@app.get("/", tags=['Healthcheck'], dependencies=[Depends(RateLimiter(times=5, seconds=30))])
def read_root():
    """## Healthchecker"""
    return {"message": "PixnTalk API is alive"}
