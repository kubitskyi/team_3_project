from sqlalchemy.orm import Session
from src.database.models import Photo, Tag
from fastapi import HTTPException
from typing import List
import shutil
import os

# Путь для сохранения загруженных фотографий
UPLOAD_DIRECTORY = "uploads/photos/"

def create_photo(db: Session, photo_url: str, photo_data):
    new_photo = Photo(url=photo_url, description=photo_data.description)
    db.add(new_photo)
    db.commit()
    db.refresh(new_photo)
    return new_photo


def delete_photo(photo_id: int, db: Session):
    # Поиск фотографии по ID
    photo = db.query(Photo).filter(Photo.id == photo_id).first()

    if not photo:
        raise HTTPException(status_code=404, detail="Фото не найдено")

    # Удаление фото с диска
    if os.path.exists(photo.file_path):
        os.remove(photo.file_path)

    # Удаление записи о фото и связанных тегов из базы данных
    db.query(Tag).filter(Tag.photo_id == photo_id).delete()
    db.delete(photo)
    db.commit()

    return {"message": "Фото удалено"}


def update_photo(photo_id: int, description: str, tags: List[str], db: Session):
    # Поиск фотографии по ID
    photo = db.query(Photo).filter(Photo.id == photo_id).first()

    if not photo:
        raise HTTPException(status_code=404, detail="Фото не найдено")

    # Обновление описания фото
    photo.description = description

    # Обновление тегов
    db.query(Tag).filter(Tag.photo_id == photo_id).delete()  # Удаляем старые теги
    for tag_name in tags:
        tag = Tag(name=tag_name, photo_id=photo_id)
        db.add(tag)

    db.commit()
    return photo


def get_photo(photo_id: int, db: Session):
    # Поиск фотографии по ID
    photo = db.query(Photo).filter(Photo.id == photo_id).first()

    if not photo:
        raise HTTPException(status_code=404, detail="Фото не найдено")

    return photo
