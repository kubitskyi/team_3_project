from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.schemas.transformations import CropAndScaleRequest
from src.database.connect import get_db
from src.database.models import User, Photo
from src.services.auth import auth_service as auth_s
from src.repository.transformations import add_transform_image
from src.services.photo_service import crop_and_scale


router = APIRouter(prefix="/img-service", tags=["Image service"])

@router.post("/crop_and_scale/{photo_id}")
def transform_image(body: CropAndScaleRequest,
                    db: Session = Depends(get_db),
                    current_user: User = Depends(auth_s.get_current_user) 
                    ):
   
    photo_id = body.photo_id
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if photo.user_id == current_user.id:
        if photo:
            url =  crop_and_scale(public_id=photo.public_id, width=body.width, height=body.height)

            return add_transform_image(image_url=url,
                                    original_photo_id=photo.id,
                                    type = crop_and_scale.__name__,
                                    db=db
                                    )
    else:
        raise