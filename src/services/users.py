"""Service file for users operations"""
from fastapi import HTTPException, status, UploadFile
import cloudinary
import cloudinary.uploader

from src.database.models import RoleEnum, User


def validate_role(role: str) -> str:
    """Validates the provided role against the allowed roles defined in `RoleEnum`.

    Args:
        role (str): The role string to be validated.

    Raises:
        HTTPException: If the provided role is not valid according to `RoleEnum`.

    Returns:
        RoleEnum object: The role that is RoleEnum objecct.
    """
    role.strip().lower()
    try:
        return RoleEnum(role)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="UserServices: Invalid role"
        ) from e

async def upload_avatar(user: User, file: UploadFile):
    """Uploads the user's avatar image to Cloudinary, and returns a URL for the uploaded image.

    Args:
        user (User): The user whose avatar is being uploaded.
        file (UploadFile): The image file to be uploaded.

    Returns:
        str: The URL of the uploaded avatar image, resized to 250x250 pixels.
    """
    r = cloudinary.uploader.upload(
        file.file,
        public_id=f'PixnTalk/{user.name}',
        overwrite=True
    )
    src_url = cloudinary.CloudinaryImage(
        f'PixnTalk/{user.name}'
    ).build_url(
        width=250,
        height=250,
        crop='fill',
        version=r.get('version')
    )
    return src_url

async def remove_avatar(user: User):
    """Removes the user's avatar from Cloudinary.

    Args:
        user (User): The user whose avatar is to be removed.

    Raises:
        HTTPException: If the avatar deletion fails, an HTTP 400 Bad Request exception
            is raised with an appropriate error message.
    """
    public_id = f'PixnTalk/{user.name}'
    result = cloudinary.uploader.destroy(public_id)
    if result.get('result') != 'ok':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to delete avatar"
        )
