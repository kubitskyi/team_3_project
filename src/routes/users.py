"""Router for work with users"""
from sqlalchemy.orm import Session
from fastapi_limiter.depends import RateLimiter
from fastapi.security import HTTPBearer
from fastapi import APIRouter, Depends, UploadFile, File

from src.database.connect import get_db
from src.database.models import User, RoleEnum
from src.routes.auth import get_redis
from src.services.auth import auth_service as auth_s
from src.services.users import upload_avatar, remove_avatar
from src.schemas.users import UserReturn, UserPublic
from src.repository.users import (
    get_user_by_name, update_avatar, delete_avatar, ban_unban, change_role,
    update_about, delete_about, count_admins
)


router = APIRouter(prefix='/user', tags=["Users"])
get_refr_token = HTTPBearer()


@router.get(
    "/{username}",
    response_model=UserPublic,
    dependencies=[Depends(RateLimiter(times=5, seconds=30))]
)
async def read_user_public(
    username: str,
    db: Session = Depends(get_db),
    redis = Depends(get_redis)
) -> UserReturn:
    """## User's public profile
    ```
    /api/user/_username_
    ```
    Retrieves public information about a user, including their online status,
    and returns the user's public profile.

    ### Args:
        username (str): The username of the user whose public information is to be retrieved.
        db (Session, optional): The database session used to query user data.
            Defaults to Depends(get_db).
        redis (_type_, optional): Redis instance used to check if the user is online.
            Defaults to Depends(get_redis).

    ### Returns:
        UserReturn: A user object containing public profile information, including
            the online status.
    """
    user = await get_user_by_name(username, db)
    token = await redis.get(f"user_token:{user.id}")
    user.is_online = bool(token)
    return user


@router.get("/profile", response_model=UserReturn)
async def read_user_profile(
    username: str,
    current_user: User = Depends(auth_s.get_current_user),
    db: Session = Depends(get_db),
    redis = Depends(get_redis)
) -> UserReturn:
    """## User's full profile
    ```
    /api/user/profile
    ```
    Retrieves the profile of a specified user if the current user has access rights and
    returns the user's full profile, including their online status.

    ### Args:
        username (str): The username of the user whose profile is to be retrieved.
        current_user (User, optional): The currently authenticated user, used to check access
            rights. Defaults to Depends(auth_s.get_current_user).
        db (Session, optional): The database session used to query user data. Defaults to
            Depends(get_db).
        redis (_type_, optional): Redis instance used to check if the user is online. Defaults to
            Depends(get_redis).

    ### Returns:
        UserReturn: The full profile of the user, including whether they are online.
    """
    owner = await get_user_by_name(username, db)
    check = await auth_s.check_access(current_user, owner.id)
    if check:
        token = await redis.get(f"user_token:{owner.id}")
        owner.is_online = bool(token)
        return owner


@router.patch('/avatar', response_model=UserReturn)
async def update_avatar_user(
    file: UploadFile = File(),
    current_user: User = Depends(auth_s.get_current_user),
    db: Session = Depends(get_db)
) -> UserReturn:
    """## Update the avatar of the current authenticated user.
    ```
    /api/user/avatar
    ```
    This endpoint allows the user to upload a new avatar image, which is stored in Cloudinary.
    The uploaded image is processed and resized, and the URL to the new avatar is saved to
    the user's profile.

    ### Args:
        file (UploadFile, optional): The avatar image file to be uploaded. Defaults to File().
            current_user (User, optional): The current authenticated user. Injected via `
            Depends(auth_s.get_current_user)`.
        db (Session, optional): The database session used to update the user. Defaults to `
            Depends(get_db)`.

    ### Returns:
        UserReturn: The updated user profile with the new avatar URL.
    """
    src_url = await upload_avatar(current_user, file)
    user = await update_avatar(current_user, src_url, db)
    return user


@router.patch('/about', response_model=UserReturn)
async def update_about_user(
    text: str,
    current_user: User = Depends(auth_s.get_current_user),
    db: Session = Depends(get_db)
) -> UserReturn:
    """## Updates the 'about' section of the current user.
    ```
    /api/user/about
    ```
    This endpoint allows the current authenticated user to update their
    'about' section with the provided text.

    ### Args:
        text (str): The new text to set in the user's 'about' section.
        current_user (User, optional): The current user object, retrieved
            using the authentication dependency. Defaults to
            Depends(auth_s.get_current_user).
        db (Session, optional): The database session used to commit the changes.
            Defaults to Depends(get_db).

    ### Returns:
        UserReturn: The updated user object containing the modified 'about' section.
    """
    user = await update_about(current_user, text, db)
    return user


@router.delete('/avatar', response_model=dict)
async def delete_avatar_user(
    username: str,
    current_user: User = Depends(auth_s.get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """## Delete user's avatar.
    ```
    /api/user/avatar
    ```
    This endpoint allows the deletion of a user's avatar image. The user who owns the
    avatar or a user with specific roles (such as moderator or admin) is authorized to
    perform this action. Once the avatar is deleted, the user's profile is updated
    to reflect the change.

    ### Args:
        username (str): The username of the user whose avatar is being deleted.
        current_user (User, optional): The currently authenticated user, injected
            via `Depends(auth_s.get_current_user)`.
        db (Session, optional): The database session used to perform operations
            on the user's avatar. Injected via `Depends(get_db)`.

    ### Returns:
        dict: A confirmation message indicating the avatar has been successfully deleted.

    ### Raises:
        HTTPException: If the current user is not the owner of the avatar and
            does not have the required roles (e.g., 'moderator', 'admin'),
            a 403 Forbidden error is raised.
    """
    owner = await get_user_by_name(username, db)
    check = await auth_s.check_access(current_user, owner.id)
    if check:
        await remove_avatar(owner)
        await delete_avatar(owner, db)
        return {"message": "Avatar deleted."}


@router.delete('/about', response_model=dict)
async def delete_about_user(
    username: str,
    current_user: User = Depends(auth_s.get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """## Deletes the 'about' section of the specified user.
    ```
    /api/user/about
    ```
    This endpoint allows the current authenticated user to delete the
    'about' section of another user specified by their username.

    ### Args:
        username (str): The username of the user whose 'about' section is to be deleted.
        current_user (User, optional): The current user object, retrieved
            using the authentication dependency. Defaults to
            Depends(auth_s.get_current_user).
        db (Session, optional): The database session used to commit the changes.
            Defaults to Depends(get_db).

    ### Returns:
        dict: A dictionary containing a message confirming that the
        'about' section has been deleted.
    """
    owner = await get_user_by_name(username, db)
    check = await auth_s.check_access(current_user, owner.id)
    if check:
        await delete_about(owner, db)
        return {"message": "Info about deleted."}


@router.patch('/admin/change_role', response_model=dict)
async def change_user_role(
    username: str,
    new_role: str,
    current_user: User = Depends(auth_s.get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """## Asynchronously changes the role of a specified user to a new role.
    ```
    /api/user/admin/change_role
    ```
    Works if the current user has **admin privileges**.

    If the current user is attempting to change their own role and is the last remaining admin,
    the role change is prevented.

    ### Args:
        username (str): The username of the user whose role is to be changed.
        new_role (str): The new role to assign to the user.
        current_user (User, optional): The currently authenticated user, used to verify admin
            privileges. Defaults to Depends(auth_s.get_current_user).
        db (Session, optional): The database session used for retrieving and updating the user.
            Defaults to Depends(get_db).

    ### Returns:
        dict: A dictionary containing a success message indicating that the role has been changed,
            or an error message if the role change was prevented.

    ### Raises:
        HTTPException: If the current user is not an admin, a 403 Forbidden error is raised.
    """
    user = await get_user_by_name(username, db)
    check = await auth_s.check_admin(current_user, [RoleEnum.admin])
    if check:
        if current_user.id == user.id:
            doublecheck = await count_admins(db)
            if doublecheck < 2:
                return {"message": "Role can't be changed. You are last Admin."}
            await change_role(user, new_role, db)
            return {"message": f"Role changed to {new_role}."}


@router.patch('/admin/ban-unban', response_model=dict)
async def ban_user(
    username: str,
    confirmation: bool,
    current_user: User = Depends(auth_s.get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """## Ban or unban a user from the system.
    ```
    /api/user/admin/ban-unban
    ```
    This endpoint allows an admin user to ban or unban another user by their username.
    If the `confirmation` flag is set to `True`, the target user is banned, and their
    access to the platform is revoked. If set to `False`, the user is unbanned.
    Only users with the role **admin** are authorized to perform this action.

    ### Args:
        username (str): The username of the user to be banned or unbanned.
        confirmation (bool): A flag indicating whether the ban should be applied (`True` to ban,
            `False` to unban).
        current_user (User, optional): The currently authenticated user, injected via
            `Depends(auth_s.get_current_user)`.
        db (Session, optional): The database session used to perform operations on the user's
            account. Injected via `Depends(get_db)`.

    ### Returns:
        dict: A message confirming whether the user has been successfully banned or unbanned.

    ### Raises:
        HTTPException: If the current user is not an admin, a 403 Forbidden error is raised.
            A message is also returned if the current user attempts to ban themselves.
    """
    user = await get_user_by_name(username, db)
    check = await auth_s.check_admin(current_user, [RoleEnum.admin])
    if check and confirmation:
        if current_user.id == user.id:
            return {"message": "You are trying to ban yourself."}
        await ban_unban(user, db)
        return {"message": "User status changed."}
