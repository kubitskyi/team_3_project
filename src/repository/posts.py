import os
import cloudinary
import cloudinary.api
from typing import List
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.services.cloudinary import delete_image
from src.database.models import Photo, Tag, User
from src.schemas.posts import PhotoResponse, PhotoUpdate




def create_photo(db: Session, 
                 photo_url: str, 
                 description,
                 tags,
                 public_id,
                 current_user: User):
    
    if not current_user:
        raise HTTPException(status_code=403, detail="Неавторизовано")
    
    new_photo = Photo(
        image_url=photo_url, 
        description=description, 
        user_id = current_user.id,
        tags=tags,
        public_id = public_id,
        updated_at = func.now()
        )
    db.add(new_photo)
    db.commit()
    db.refresh(new_photo)
    response_data = PhotoResponse(
        id=new_photo.id,
        description=new_photo.description,
        image_url=new_photo.image_url,
        user_id=new_photo.user_id,
        tags=[tag.name for tag in new_photo.tags],  # Якщо tag — це об'єкт, повертаємо його name
        created_at=new_photo.created_at,
        updated_at=new_photo.updated_at
    )
    return response_data


def delete_photo(photo_id: int, db: Session):
    # Поиск фотографии по ID
    photo = db.query(Photo).filter(Photo.id == photo_id).first()

    if not photo:
        raise HTTPException(status_code=404, detail="Фото не найдено")
        
    try:
        result = delete_image(photo.public_id)
    except cloudinary.exceptions.NotFound as e:
        print(e)
    if result:
        db.query(Photo).filter(Photo.id == photo.id).delete()
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
    photo.tags = tags
    
    # Обновление тегов
    # db.query(Tag).filter(Tag.photo_id == photo_id).delete()  # Удаляем старые теги
    # for tag_name in tags:
    #     tag = Tag(name=tag_name, photo_id=photo_id)
    #     db.add(tag)

    db.commit()
    # response_data = {**photo}
    # response_data['tags'] = [tag.name for tag in photo.tags]
    response_data =  {
        "description": photo.description,
        "image_url": photo.image_url,
        "tags": [tag.name for tag in photo.tags]
    }
    return response_data


def get_photo(photo_id: int, db: Session):
    # Поиск фотографии по ID
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Фото не найдено")

    response_data = PhotoResponse(
        id=photo.id,
        description=photo.description,
        image_url=photo.image_url,
        user_id=photo.user_id,
        tags=[tag.name for tag in photo.tags],  # Якщо tag — це об'єкт, повертаємо його name
        created_at=photo.created_at,
        updated_at=photo.updated_at
    )
    return response_data
