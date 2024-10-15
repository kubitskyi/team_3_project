from typing import List
import cloudinary
import cloudinary.api
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.services.photo_service import delete_image
from src.database.models import Photo, User, PhotoRating, Tag
from src.schemas.posts import PhotoResponse, PhotoUpdate
from src.templates.message import PHOTO_NOT_FOUND, SUCCESSFUL_ADD_RATE



def create_photo(
    db: Session,
    photo_url: str,
    description,
    tags,
    public_id,
    current_user: User
):

    if not current_user:
        raise HTTPException(status_code=403, detail="Not autorized")

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
        average_rating=new_photo.average_rating,
        tags=[tag.name for tag in new_photo.tags],  # Якщо tag — це об'єкт, повертаємо його name
        created_at=new_photo.created_at,
        updated_at=new_photo.updated_at
    )
    return response_data


def delete_photo(photo_id: int, db: Session):
    # Поиск фотографии по ID
    photo = db.query(Photo).filter(Photo.id == photo_id).first()

    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    try:
        result = delete_image(photo.public_id)
    except cloudinary.exceptions.NotFound as e:
        print(e)
    if result:
        db.query(Photo).filter(Photo.id == photo.id).delete()
        db.delete(photo)
        db.commit()
    return {"message": "Фото удалено"}


def update_photo(photo_id: int, description: str, tags: List[Tag], db: Session):
    # Поиск фотографии по ID
    photo = db.query(Photo).filter(Photo.id == photo_id).first()

    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    # Обновление описания фото
    photo.description = description
    photo.tags = tags
    db.commit()
    db.refresh(photo)
    
    response_data =  {
        "id": photo.id,
        "description": photo.description,
        "image_url": photo.image_url,
        "tags": [tag.name for tag in photo.tags]
    }
    return response_data


def get_photo(photo_id: int, db: Session):
    # Поиск фотографии по ID
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if not photo:
        raise HTTPException(status_code=404, detail=PHOTO_NOT_FOUND)

    response_data = PhotoResponse(
        id=photo.id,
        description=photo.description,
        image_url=photo.image_url,
        user_id=photo.user_id,
        average_rating=photo.average_rating,
        tags=[tag.name for tag in photo.tags],  # Якщо tag — це об'єкт, повертаємо його name
        created_at=photo.created_at,
        updated_at=photo.updated_at
    )
    return response_data

def add_rate(user, photo_id, rate, db: Session):
    # Додавання нового рейтингу для фото
    db_rating = db.query(PhotoRating).filter(
        PhotoRating.user_id==user.id,
        PhotoRating.photo_id==photo_id
    ).first()
    print(db_rating)
    if db_rating:
        print(f"Rate:{rate}")
        db_rating.rating=rate
    else:
        db_rating = PhotoRating(user_id=user.id, photo_id=photo_id, rating=rate)  # user_id не врах
    db.add(db_rating)
    db.commit()
    db.refresh(db_rating)

    # Оновлення середнього рейтингу
    update_photo_average_rating(photo_id, db)
    return SUCCESSFUL_ADD_RATE


def update_photo_average_rating(photo_id: int, db: Session):
    ratings = db.query(PhotoRating).filter_by(photo_id=photo_id).all()
    if ratings:
        average = sum(rating.rating for rating in ratings) / len(ratings)
    else:
        average = 0

    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    photo.average_rating = average
    db.commit()
