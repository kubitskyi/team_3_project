"""Router for work with users"""
import cloudinary
import cloudinary.uploader
from sqlalchemy.orm import Session
# from fastapi_limiter.depends import RateLimiter
from fastapi.security import HTTPBearer
from fastapi import (
    APIRouter, Depends, UploadFile, File
)

from src.database.connect import get_db
from src.database.models import User
from src.routes.auth import get_redis
from src.services.auth import auth_service as auth_s
from src.schemas.users import UserReturn
from src.repository.users import (
    get_user_by_name, update_avatar, delete_avatar, ban_offender
)


router = APIRouter(prefix='/users', tags=["Users"])
get_refr_token = HTTPBearer()


@router.get("/user", response_model=UserReturn)
async def read_users_me(
    current_user: User = Depends(auth_s.get_current_user),
    redis = Depends(get_redis)
) -> UserReturn:
    """Get the current authenticated user's details.

    This endpoint retrieves the information of the currently authenticated user.
    The user's details are returned in the response model format `UserReturn`.

    Args:
        current_user (User, optional): The current authenticated user.
            It is automatically injected by the `Depends(auth_s.get_current_user)` function.

    Returns:
        UserReturn: A model representing the authenticated user's details.
    """
    token = await redis.get(f"user_token:{current_user.id}")
    current_user.is_online = bool(token)
    return current_user


@router.patch('/user/avatar', response_model=UserReturn)
async def update_avatar_user(
    file: UploadFile = File(),
    current_user: User = Depends(auth_s.get_current_user),
    db: Session = Depends(get_db)
) -> UserReturn:
    """Update the avatar of the current authenticated user.

    This endpoint allows the user to upload a new avatar image, which is stored in Cloudinary.
    The uploaded image is processed and resized, and the URL to the new avatar is saved to
    the user's profile.

    Args:
        file (UploadFile, optional): The avatar image file to be uploaded. Defaults to File().
            current_user (User, optional): The current authenticated user. Injected via `
            Depends(auth_s.get_current_user)`.
        db (Session, optional): The database session used to update the user. Defaults to `
            Depends(get_db)`.

    Returns:
        UserReturn: The updated user profile with the new avatar URL.
    """
    r = cloudinary.uploader.upload(
        file.file,
        public_id=f'PixnTalk/{current_user.name}',
        overwrite=True
    )
    src_url = cloudinary.CloudinaryImage(
        f'PixnTalk/{current_user.name}'
    ).build_url(
        width=250,
        height=250,
        crop='fill',
        version=r.get('version')
    )
    user = await update_avatar(current_user.email, src_url, db)
    return user


@router.delete('/user/avatar', response_model=dict)
async def delete_avatar_user(
    username: str,
    current_user: User = Depends(auth_s.get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """Delete a user's avatar.

    This endpoint allows the deletion of a user's avatar image. The user who owns the
    avatar or a user with specific roles (such as moderator or admin) is authorized to
    perform this action. Once the avatar is deleted, the user's profile is updated
    to reflect the change.

    Args:
        username (str): The username of the user whose avatar is being deleted.
        current_user (User, optional): The currently authenticated user, injected
            via `Depends(auth_s.get_current_user)`.
        db (Session, optional): The database session used to perform operations
            on the user's avatar. Injected via `Depends(get_db)`.

    Returns:
        dict: A confirmation message indicating the avatar has been successfully deleted.

    Raises:
        HTTPException: If the current user is not the owner of the avatar and
            does not have the required roles (e.g., 'moderator', 'admin'),
            a 403 Forbidden error is raised.
    """
    owner = await get_user_by_name(username, db)
    check = await auth_s.check_access(current_user, owner.id)
    if check:
        await delete_avatar(owner, db)
        return {"message": "Avatar deleted."}


@router.patch('/user/ban', response_model=dict)
async def ban_user(
    username: str,
    confirmation: bool,
    current_user: User = Depends(auth_s.get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """Ban a user from the system.

    This endpoint allows an admin user to ban another user by their username. If the
    `confirmation` flag is set to `True`, the target user is banned, and their access
    to the platform is revoked. Only users with the role 'admin' are authorized to perform
    this action.

    Args:
        username (str): The username of the user to be banned.
        confirmation (bool): A confirmation flag indicating whether the ban should be applied.
        current_user (User, optional): The currently authenticated user, injected via
            `Depends(auth_s.get_current_user)`.
        db (Session, optional): The database session used to perform operations
            on the user's account. Injected via `Depends(get_db)`.

    Returns:
        dict: A confirmation message indicating the user has been successfully banned.

    Raises:
        HTTPException: If the current user is not an admin, a 403 Forbidden error is raised.
    """
    offender = await get_user_by_name(username, db)
    check = await auth_s.check_admin(current_user, ['admin'])
    if check and confirmation:
        await ban_offender(offender, db)
        return {"message": "Avatar deleted."}
