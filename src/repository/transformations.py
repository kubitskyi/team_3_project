from sqlalchemy.orm import Session
from src.database.models import PhotoTransformation
from src.schemas.transformations import PhotoTransformationResponse


def add_transform_image(image_url, type, original_photo_id, db: Session,):
   
    new_photo = PhotoTransformation(
        original_photo_id=original_photo_id,
        transformation_type=type,
        image_url = image_url
        )
    db.add(new_photo)
    db.commit()
    db.refresh(new_photo)
        
    response = PhotoTransformationResponse(
        id = new_photo.id,
        original_photo_id = new_photo.original_photo_id,
        transformation_type = new_photo.transformation_type,
        image_url = new_photo.image_url,
        created_at = new_photo.created_at
        )
    
    return response