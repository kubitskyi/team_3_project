"""Router to use transformations to photo"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse
from src.schemas.transformations import CropAndScaleRequest
from src.database.connect import get_db
from src.database.models import User, Photo, PhotoTransformation
from src.services.auth import auth_service as auth_s
from src.repository.transformations import add_transform_image
from src.services.photo_service import crop_and_scale, generate_qr_code
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


@router.post("/get-qrcode-link/{photo_id}")
def get_qrcode_link(photo_id, db: Session = Depends(get_db),current_user: User = Depends(auth_s.get_current_user)):
    """
    Generates a QR code link for the image associated with the given photo_id.

    - Verifies if the current user is the owner of the photo.
    - If the check passes, it generates a QR code for the image URL.
    - Returns the QR code in PNG format.

    Args:
        photo_id (int): The identifier of the transformed photo.
        db (Session): Database session provided through dependency injection.
        current_user (User): The currently authenticated user provided through dependency injection.

    Raises:
        HTTPException: If the user is not the owner of the photo or if there is an error generating the QR code.

    Returns:
        StreamingResponse: The QR code image in PNG format.
    """
    photo = db.query(PhotoTransformation).filter(PhotoTransformation.id == photo_id).first()
    original_photo = db.query(Photo).filter(Photo.id == photo.original_photo_id).first()
    if current_user.id != original_photo.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=OWNER_CHECK_ERROR_MSG)
    try:
        response = generate_qr_code(photo.image_url)
        return StreamingResponse(response, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))