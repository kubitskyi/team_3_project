from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List
import uuid
import pathlib
import cloudinary
from sqlalchemy.orm import Session
from src.database.connect import SessionLocal
from src.schemas.posts import PhotoResponse, PhotoUpload
from src.repository import posts as posts_crud

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/photo/", response_model=PhotoResponse)
async def upload_photo(file: UploadFile = File(...), description: str = "No description", db: Session = Depends(get_db)):
     # Створення унікального імені для файлу
    unique_filename = str(uuid.uuid4()) + pathlib.Path(file.filename).suffix

    # Завантаження файлу на Cloudinary
    try:
        upload_result = cloudinary.uploader.upload(file.file, public_id=unique_filename)
        photo_url = upload_result["url"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка завантаження на Cloudinary: {str(e)}")

    # Збереження інформації про фото в базу даних
    photo_data = PhotoResponse(description=description)
    new_photo = posts_crud.create_photo(db=db, photo_url=photo_url, photo_data=photo_data)

    return new_photo
    
   
@router.delete("/photo/{photo_id}", response_model=PhotoResponse)
async def delete_photo(photo_id: int, db: Session = Depends(get_db)):
    return posts_crud.delete_photo(photo_id, db)

@router.put("/photo/{photo_id}", response_model=PhotoResponse)
async def update_photo(photo_id: int, description: str, tags: List[str] = [], db: Session = Depends(get_db)):
    return posts_crud.update_photo(photo_id, description, tags, db)

@router.get("/photo/{photo_id}", response_model=PhotoResponse)
async def get_photo(photo_id: int, db: Session = Depends(get_db)):
    return posts_crud.get_photo(photo_id, db)
