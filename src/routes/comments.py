"""Router for work with comments"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas.comments import CommentCreate, CommentUpdate, CommentResponse
from src.repository.comments import (
    create_comment, update_comment, delete_comment, get_comments_by_photo
)
from src.database.connect import get_db
from src.services.auth import auth_service as auth_s
from src.templates.message import DELETE_COMMENT_ACCESS_ERROR


router = APIRouter(prefix="/comments", tags=["Comments"])


@router.post("/", response_model=CommentResponse)
def create_new_comment(
    photo_id: int,
    comment: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_s.get_current_user)
):
    """## Creates a new comment on a specific photo.
    ```
    /api/comments/
    ```
    This endpoint allows an authenticated user to add a comment to a specified photo. The comment
    details, including its content, are provided in the `CommentCreate` object, while the photo
    is identified by its unique `photo_id`. The current user is automatically assigned as the author
    of the comment.

    ### Args:
        photo_id (int): The unique identifier of the photo to which the comment is being added.
        comment (CommentCreate): An object containing the details of the comment (e.g., content).
        db (Session, optional): The database session used for creating the comment.
            Defaults to Depends(get_db).
        current_user (User, optional): The currently authenticated user, who will be set as the
            author of the comment. Defaults to Depends(auth_s.get_current_user).

    ### Returns:
        CommentResponse: An object containing the newly created comment's details, such as the
        comment content, author, and the associated photo.
    """
    return create_comment(db, author_id=current_user.id, photo_id=photo_id, comment=comment)

@router.put("/{comment_id}", response_model=CommentResponse)
def update_existing_comment(
    comment_id: int,
    comment: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_s.get_current_user)
):
    """## Updates an existing comment made by the current user.
    ```
    /api/comments/_comment_id_
    ```
    This endpoint allows the authenticated user to update one of their existing comments.
    The comment is identified by its `comment_id`, and the updated content is provided in the
    `CommentUpdate` object. The user must be the author of the comment to modify it.

    ### Args:
        comment_id (int): The unique identifier of the comment to be updated.
        comment (CommentUpdate): An object containing the updated content of the comment.
        db (Session, optional): The database session used for retrieving and updating the comment.
            Defaults to Depends(get_db).
        current_user (User, optional): The currently authenticated user, verified as the author of
            the comment. Defaults to Depends(auth_s.get_current_user).

    ### Returns:
        CommentResponse: An object containing the updated comment details, including the new content
        and metadata.

    ### Raises:
        HTTPException: If the user is not the author of the comment or the comment is not found,
        an error will be raised.
    """
    return update_comment(db, comment_id=comment_id, author_id=current_user.id, comment=comment)

@router.delete("/{comment_id}", response_model=dict)
def delete_existing_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_s.get_current_user)
):
    """## Deletes an existing comment if the current user has admin or moderator privileges.
    ```
    /api/comments/_comment_id_
    ```
    This endpoint allows an admin or moderator to delete a comment by specifying its `comment_id`.
    Only users with the appropriate permissions **(admin or moderator)** can perform this action.

    ### Args:
        comment_id (int): The unique identifier of the comment to be deleted.
        db (Session, optional): The database session used to find and delete the comment.
            Defaults to Depends(get_db).
        current_user (User, optional): The currently authenticated user, checked for admin
            or moderator privileges. Defaults to Depends(auth_s.get_current_user).

    ### Raises:
        HTTPException: If the current user does not have admin or moderator privileges, a 400
        Bad Request error is raised.

    ### Returns:
        dict: A confirmation message indicating that the comment was successfully deleted.
    """
    if  auth_s.check_admin(user = current_user.id):
        return delete_comment(db, comment_id=comment_id)
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=DELETE_COMMENT_ACCESS_ERROR
    )

@router.get("/post/{photo_id}", response_model=List[CommentResponse])
def get_comments_for_photo(photo_id: int, db: Session = Depends(get_db)):
    """## Retrieves a list of comments for a specified photo.
    ```
    /api/comments/post/_photo_id_
    ```
    This endpoint allows users to fetch all comments associated with a specific photo
    by providing the photo's unique identifier (`photo_id`). The comments are returned
    in a list and formatted according to the `CommentResponse` model.

    ### Args:
        photo_id (int): The unique identifier of the photo for which to retrieve comments.
        db (Session, optional): The database session used to query and retrieve comments.
            Defaults to Depends(get_db).

    ### Returns:
        List[CommentResponse]: A list of comments related to the specified photo, formatted
        according to the `CommentResponse` schema.
    """
    return get_comments_by_photo(db, photo_id=photo_id)
