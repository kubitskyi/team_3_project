from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.schemas.transformations import CropAndScaleRequest
from src.database.connect import get_db
from src.database.models import User, Photo
from src.services.auth import auth_service as auth_s


router = APIRouter(prefix="/img-service", tags=["Image service"])

@router.post("/crop_and_scale/{photo_id}", response_model=CropAndScaleRequest)
def transform_image(body: CropAndScaleRequest,
                    db: Session = Depends(get_db),
                    
                    ):
    # current_user: User = Depends(auth_s.get_current_user) 
    print("==="*20)
    print(body)
    photo_id = body.photo_id
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if photo:
        return {"msg": True}
    return {"msg": False}