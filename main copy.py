from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, UploadFile
import uvicorn
import cloudinary
import redis.asyncio as redis
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from src.conf.config import settings
from src.routes import auth
from src.routes import users
from src.routes import posts
from src.routes import comments
from sqlalchemy.orm import Session
from src.database import get_db
from src.database.models import PhotoLink
from src.database.photo_service import upload_image_to_cloudinary, transform_image, generate_qr_code


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
    cloudinary_config

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

app = FastAPI()

@app.post("/upload/")
async def upload_image(file: UploadFile, db: Session = Depends(get_db)):
    
    original_url, public_id = upload_image_to_cloudinary(file.file)

    
    transformed_url = transform_image(public_id)

    
    qr_code_img = generate_qr_code(transformed_url)
    
    
    with open("qr_code.png", "wb") as f:
        f.write(qr_code_img.read())

    
    photo_link = PhotoLink(
        original_url=original_url,
        transformed_url=transformed_url,
        qr_code_url="path_to_saved_qr_code"
    )
    db.add(photo_link)
    db.commit()

    return {"original_url": original_url, "transformed_url": transformed_url, "qr_code_url": "path_to_saved_qr_code"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="localhost",
        port=8000,
        reload=True
    )
