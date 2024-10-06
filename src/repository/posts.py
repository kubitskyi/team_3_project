from sqlalchemy.orm import Session
from src.database.models import Photo, Tag
from fastapi import HTTPException
from typing import List

def create_photo(file, description: str, tags: List[str], db: Session):
    # Логіка для завантаження фото та створення запису в базі
    pass

def delete_photo(photo_id: int, db: Session):
    # Логіка для видалення фото
    pass

def update_photo(photo_id: int, description: str, tags: List[str], db: Session):
    # Логіка для оновлення фото
    pass

def get_photo(photo_id: int, db: Session):
    # Логіка для отримання фото за ID
    pass
