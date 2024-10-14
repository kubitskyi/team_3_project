"""Router for work with posts"""
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from sqlalchemy.orm import Session

from src.database.connect import  get_db
from src.database.models import  User, Tag, Photo
from src.schemas.posts import PhotoResponse, PhotoCreate, PhotoUpdate
from src.repository import posts as posts_crud
from src.services.photo_service import  upload_file
from src.services.auth import auth_service


router = APIRouter(prefix="/posts", tags=["Posts"])


@router.post("/photo", response_model=PhotoCreate)
async def upload_photo(
    file: UploadFile = File(...),
    description: str = "No description",
    db: Session = Depends(get_db),
    tags: List[str] | None = None,
    current_user: User = Depends(auth_service.get_current_user)
):
    """Uploads a photo to Cloudinary, associates it with the current user, and optionally tags it.

    This endpoint allows a user to upload a photo, which is saved in Cloudinary. The user can also
    provide a description and up to 5 tags that categorize the photo. If any of the tags do not
    exist, they will be created in the database.

    Args:
        file (UploadFile, optional): The image file to be uploaded. Required.
        description (str, optional): A description for the photo. Defaults to "No description".
        db (Session, optional): The database session used to interact with the database.
            Defaults to Depends(get_db).
        tags (List[str], optional): A list of tags for the photo, separated by commas. Defaults
            to an empty list.
        current_user (User, optional): The currently authenticated user uploading the photo.
            Defaults to Depends(auth_service.get_current_user).

    Raises:
        HTTPException: Raised with status 400 if more than 5 tags are provided.

    Returns:
        PhotoCreate: The newly created photo object containing the photo URL, public ID,
            description, and tags.
    """
    if not tags:
        tags = []
    photo_url, public_id = upload_file(file)

    tags_list = []
    if len(tags) > 0:
        tags_list = tags[0].split(",")

    if len(tags_list) > 5:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="Too many tags. Available only 5 tags."
        )

    tags = []
    for tag in tags_list:
        new_tag = db.query(Tag).filter(Tag.name==tag).one_or_none()
        if new_tag is None:
            new_tag = Tag(name=tag)
            db.add(new_tag)
            db.commit()
        tags.append(new_tag)

    new_photo = posts_crud.create_photo(
        db=db,
        photo_url=photo_url,
        tags=tags,public_id=public_id,
        description=description,current_user=current_user
    )
    return new_photo


@router.delete("/photo/{photo_id}", response_model=dict)
async def delete_photo(
    photo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """Deletes a photo by its ID if the current user is authorized.

    This endpoint allows a user to delete a photo they own. If the current user is the owner of the
    photo, moderator or admin, the photo is removed from the database. Otherwise, a
    `400 Bad Request` is raised due to insufficient authorization.

    Args:
        photo_id (int): The ID of the photo to be deleted.
        db (Session, optional): The database session for querying and deleting the photo.
            Defaults to Depends(get_db).
        current_user (User, optional): The currently authenticated user trying to delete the photo.
            Defaults to Depends(auth_service.get_current_user).

    Raises:
        HTTPException: Raised with status 400 if the user is not authorized to delete the photo,
            or if the photo does not exist.

    Returns:
        dict: A dictionary confirming that the photo has been successfully deleted, or
            appropriate error messages.
    """
    photo = db.query(Photo).filter(Photo.id == photo_id).one_or_none()
    if  auth_service.check_access(user = current_user.id, owner_id=photo.user_id):
        return posts_crud.delete_photo(photo_id, db)
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Not authorized",
    )


@router.put("/photo/{photo_id}", response_model=PhotoUpdate)
async def update_photo(
    photo_id: int,
    description: str = "No description",
    db: Session = Depends(get_db),
    tags: List[str] | None = None,
    current_user: User = Depends(auth_service.get_current_user)
):
    """Updates a photo's description and tags if the current user is authorized.

    This endpoint allows the owner of a photo, admin and moderator to update its description and
    associated tags. If the user provides new tags that do not already exist, they will be created
    in the database.
    A maximum of 5 tags can be assigned to each photo. The operation is allowed only if the
    current user is the owner of the photo.

    Args:
        photo_id (int): The ID of the photo to be updated.
        description (str, optional): The new description for the photo. Defaults to
            "No description".
        db (Session, optional): The database session used for retrieving and updating the photo.
            Defaults to Depends(get_db).
        tags (List[str], optional): A list of tags to associate with the photo. Tags should be
            separated by commas. Defaults to an empty list.
        current_user (User, optional): The currently authenticated user attempting to update
            the photo. Defaults to Depends(auth_service.get_current_user).

    Raises:
        HTTPException: Raised with status 400 if the user is not authorized to update the photo or
            if more than 5 tags are provided.
        HTTPException: Raised with status 404 if the photo does not exist.

    Returns:
        PhotoUpdate: The updated photo object containing the new description and tags.
    """
    if not tags:
        tags = []
    photo = db.query(Photo).filter(Photo.id == photo_id).one_or_none()
    if  auth_service.check_access(user = current_user.id, owner_id=photo.user_id):
        tags_list = []
        if len(tags) > 0:
            tags_list = tags[0].split(",")

        if len(tags_list) > 5:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail="Too many tags. Available only 5 tags."
            )
        tags = []
        for tag in tags_list:
            new_tag = db.query(Tag).filter(Tag.name==tag).one_or_none()
            if new_tag is None:
                new_tag = Tag(name=tag)
                db.add(new_tag)
                db.commit()
                print("%"*30)
                print(new_tag.id)
            tags.append(new_tag)
        return posts_crud.update_photo(photo_id, description, tags, db)
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Not authorized",
    )

@router.get("/photo/{photo_id}", response_model=PhotoResponse)
async def get_photo(photo_id: int, db: Session = Depends(get_db)):
    """Retrieves a photo by its ID.

    This endpoint fetches and returns the details of a photo from the database using its unique ID.
    The photo's metadata, such as description, tags, and upload date, is returned in the response.

    Args:
        photo_id (int): The unique identifier of the photo to retrieve.
        db (Session, optional): The database session used for querying the photo.
            Defaults to Depends(get_db).

    Returns:
        PhotoResponse: An object containing the photo's details such as URL, description, tags,
        and other related information.

    Raises:
        HTTPException: If the photo does not exist, a 404 Not Found error is raised.
    """
    return posts_crud.get_photo(photo_id, db)


@router.post("/photo/{photo_id}/rate", response_model=dict)
async def add_rate(
    photo_id: int,
    rate: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """Add a rating to a specified photo.

    This endpoint allows a user to add a rating to a photo. The rating value must be
    between 1 and 5, inclusive. The user must be authenticated, and the photo must
    exist in the system. If the photo belongs to the current user, the function simply
    returns a success message without adding a rating.

    Args:
        photo_id (int): The unique identifier of the photo being rated.
        rate (int): The rating value for the photo (between 1 and 5).
        db (Session, optional): The database session used to retrieve the photo and
            perform the rating operation. Defaults to Depends(get_db).
        current_user (User, optional): The authenticated user adding the rating.
            Defaults to Depends(auth_service.get_current_user).

    Raises:
        HTTPException: Raised with a 400 status code if the rating is out of the valid range.
        HTTPException: Raised with a 404 status code if the photo is not found in the system.

    Returns:
        dict: A success message indicating that the rating has been assigned or skipped
        if the current user is the owner of the photo.
    """
    db_photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if rate < 1 or rate > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")

    if not db_photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    if db_photo.user_id != current_user.id:
        return posts_crud.add_rate(user=current_user, photo_id=photo_id, rate=rate, db=db)
    return {"message": "The rating has been successfully assigned!"}
