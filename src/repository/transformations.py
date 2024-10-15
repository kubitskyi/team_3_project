"""CRUD ops with base for photo transformations"""
from sqlalchemy.orm import Session

from src.database.models import PhotoTransformation
from src.schemas.transformations import PhotoTransformationResponse


def add_transform_image(image_url, type, original_photo_id, db: Session,):
    """Add a new image transformation entry in the database.

    This function creates a new record for an image transformation in the database,
    linking it to the original photo by its ID.

    Args:
        image_url (str): The URL of the transformed image.
        type (str): The type of transformation applied (e.g., crop, scale).
        original_photo_id (int): The ID of the original photo being transformed.
        db (Session): The database session for executing queries.

    Returns:
        PhotoTransformationResponse: The response model containing the transformation details.
    """
    new_photo = PhotoTransformation(
        original_photo_id=original_photo_id,
        transformation_type=type,
        image_url=image_url
        )
    db.add(new_photo)
    db.commit()
    db.refresh(new_photo)
    response = PhotoTransformationResponse(
        id=new_photo.id,
        original_photo_id=new_photo.original_photo_id,
        transformation_type=new_photo.transformation_type,
        image_url=new_photo.image_url,
        created_at=new_photo.created_at
        )
    return response
