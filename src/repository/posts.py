"""CRUD ops with base for posts"""
from typing import List
import cloudinary
import cloudinary.api
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.services.photo_service import delete_image
from src.database.models import Photo, User, PhotoRating, Tag
from src.schemas.posts import PhotoResponse
from src.templates.message import PHOTO_NOT_FOUND, SUCCESSFUL_ADD_RATE


def create_photo(
    db: Session,
    photo_url: str,
    description,
    tags,
    public_id,
    current_user: User
):
    """Create a new photo entry in the database.

    This function adds a new photo to the database, associated with the current user.
    If the user is not authorized, a 403 HTTP exception is raised.

    Args:
        db (Session): The database session for executing queries.
        photo_url (str): The URL of the uploaded photo.
        description (str): A description of the photo.
        tags (List[str]): A list of tags associated with the photo.
        public_id (str): The public ID of the photo in Cloudinary.
        current_user (User): The user creating the photo.

    Raises:
        HTTPException: If the user is not authorized.

    Returns:
        PhotoResponse: The response model containing the created photo details.
    """
    if not current_user:
        raise HTTPException(status_code=403, detail="Not authorized")

    new_photo = Photo(
        image_url=photo_url,
        description=description,
        user_id=current_user.id,
        tags=tags,
        public_id=public_id,
        updated_at=func.now()
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
        tags=[tag.name for tag in new_photo.tags],
        created_at=new_photo.created_at,
        updated_at=new_photo.updated_at
    )
    return response_data


def delete_photo(photo_id: int, db: Session):
    """Delete a photo from the database and Cloudinary.

    This function deletes a photo identified by its ID. If the photo is not found,
    a 404 HTTP exception is raised. It also attempts to delete the photo from Cloudinary
    and will print an error message if the Cloudinary image is not found.

    Args:
        photo_id (int): The ID of the photo to delete.
        db (Session): The database session for executing queries.

    Raises:
        HTTPException: If the photo with the specified ID does not exist.

    Returns:
        dict: A confirmation message indicating the photo has been deleted.
    """
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
    return {"message": "Photo deleted"}


def update_photo(photo_id: int, description: str, tags: List[str], db: Session):
    """Update the details of a photo.

    This function updates the description and tags of a photo identified by its ID.
    If the photo is not found, a 404 HTTP exception is raised. The existing tags are
    deleted, and new tags are added.

    Args:
        photo_id (int): The ID of the photo to update.
        description (str): The new description for the photo.
        tags (List[str]): A list of new tags to associate with the photo.
        db (Session): The database session for executing queries.

    Raises:
        HTTPException: If the photo with the specified ID does not exist.


    Returns:
        dict: A dictionary containing the updated photo details including the description,
            image URL, and tags.
    """
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
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
    """Retrieve a photo by its ID.

    This function queries the database for a photo with the specified ID.
    If found, it returns the photo's details in a structured response.
    If not found, it raises a 404 HTTP exception.

    Args:
        photo_id (int): The ID of the photo to retrieve.
        db (Session): The database session for executing queries.

    Raises:
        HTTPException: If the photo with the specified ID does not exist.

    Returns:
        PhotoResponse: A Pydantic model containing the details of the photo.
    """
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if not photo:
        raise HTTPException(status_code=404, detail=PHOTO_NOT_FOUND)
    response_data = PhotoResponse(
        id=photo.id,
        description=photo.description,
        image_url=photo.image_url,
        user_id=photo.user_id,
        average_rating=photo.average_rating,
        tags=[tag.name for tag in photo.tags],
        created_at=photo.created_at,
        updated_at=photo.updated_at
    )
    return response_data


def add_rate(user, photo_id, rate, db: Session):
    """Add or update a rating for a specific photo by a user.

    This function checks if a user has already rated the specified photo.
    If the user has rated the photo, it updates the existing rating.
    If not, it creates a new rating entry. After adding or updating the rating,
    it also updates the average rating of the photo.

    Args:
        user (User): The user who is rating the photo.
        photo_id (int): The ID of the photo to be rated.
        rate (int): The rating given by the user (should be between 1 and 5).
        db (Session): The database session for executing queries.

    Returns:
        str: A success message indicating the rating has been successfully added or updated.

    Raises:
        HTTPException: If the rating is not within the valid range (1 to 5).
        HTTPException: If the photo with the specified ID does not exist.
    """
    db_rating = db.query(PhotoRating).filter(
        PhotoRating.user_id==user.id,
        PhotoRating.photo_id==photo_id
    ).first()
    print(db_rating)
    if db_rating:
        print(f"Rate:{rate}")
        db_rating.rating=rate
    else:
        db_rating = PhotoRating(user_id=user.id, photo_id=photo_id, rating=rate)
    db.add(db_rating)
    db.commit()
    db.refresh(db_rating)
    update_photo_average_rating(photo_id, db)
    return SUCCESSFUL_ADD_RATE


def update_photo_average_rating(photo_id: int, db: Session):
    """Update the average rating of a photo based on its associated ratings.

    Args:
        photo_id (int): The ID of the photo for which the average rating is to be updated.
        db (Session): The database session used for querying and committing changes.

    Returns:
        None: This function does not return a value. It updates the average rating in the database.

    Raises:
        HTTPException: If the photo with the given ID does not exist.
    """
    ratings = db.query(PhotoRating).filter_by(photo_id=photo_id).all()
    if ratings:
        average = sum(rating.rating for rating in ratings) / len(ratings)
    else:
        average = 0
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    photo.average_rating = average
    db.commit()
