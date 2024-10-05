from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List
from sqlalchemy.orm import Session
from src.database.connect import SessionLocal
from src.schemas.posts import PhotoResponse
from src.repository import posts as posts_crud

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/photos/", response_model=PhotoResponse)
async def upload_photo(file: UploadFile, description: str, tags: List[str] = [], db: Session = Depends(get_db)):
    return posts_crud.create_photo(file, description, tags, db)

@router.delete("/photos/{photo_id}", response_model=PhotoResponse)
async def delete_photo(photo_id: int, db: Session = Depends(get_db)):
    return posts_crud.delete_photo(photo_id, db)

@router.put("/photos/{photo_id}", response_model=PhotoResponse)
async def update_photo(photo_id: int, description: str, tags: List[str] = [], db: Session = Depends(get_db)):
    return posts_crud.update_photo(photo_id, description, tags, db)

@router.get("/photos/{photo_id}", response_model=PhotoResponse)
async def get_photo(photo_id: int, db: Session = Depends(get_db)):
    return posts_crud.get_photo(photo_id, db)
