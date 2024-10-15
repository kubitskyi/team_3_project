"""Router to use transformations to photo"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.schemas.transformations import CropAndScaleRequest
from src.database.connect import get_db
from src.database.models import User, Photo
from src.services.auth import auth_service as auth_s
from src.repository.transformations import add_transform_image
from src.services.photo_service import crop_and_scale
from src.templates.message import OWNER_CHECK_ERROR_MSG


router = APIRouter(prefix="/img-service", tags=["Image service"])

@router.post("/crop_and_scale/{photo_id}")
def transform_image(
    body: CropAndScaleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_s.get_current_user)
):
    """## Crop and scale an image based on the user's input and store the transformed image link.
    ```
    /api/img-service/crop_and_scale/_photo_id_
    ```
    This function handles cropping and scaling of an image based on the provided **photo ID**
    and dimensions (`width` and `height`). The image is transformed using Cloudinary
    transformations. The link to the transformed image is stored in the database for future use.

    ### Args:
        `body` (`CropAndScaleRequest`): The request body containing the photo ID and dimensions
            for cropping and scaling.
        `db` (`Session`, optional): The database session, used to query and store data.
        `current_user` (`User`, optional): The currently authenticated user, used for permission
            checks.

    ### Returns:
        `dict`: The response containing the transformed image link and other related data.

    ### Raises:
        `HTTPException`: If the user does not own the photo or if the photo is not found in
            the database.
    """

    photo_id = body.photo_id
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if photo.user_id == current_user.id:
        if photo:
            url =  crop_and_scale(public_id=photo.public_id, width=body.width, height=body.height)
            return add_transform_image(
                image_url=url,
                original_photo_id=photo.id,
                type = crop_and_scale.__name__,
                db=db
            )
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=OWNER_CHECK_ERROR_MSG)
