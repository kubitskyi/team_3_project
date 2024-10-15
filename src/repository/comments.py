"""CRUD ops with base for comments"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from src.database.models import Comment
from src.schemas.comments import CommentCreate, CommentUpdate
from src.templates.message import COMMENT_NOT_FOUND, COMMENT_DEL


def create_comment(db: Session, author_id: int, photo_id: int, comment: CommentCreate):
    """Create a new comment associated with a specific photo.

    Args:
        db (Session): The database session used for interacting with the database.
        author_id (int): The ID of the user who is creating the comment.
        photo_id (int): The ID of the photo the comment is associated with.
        comment (CommentCreate): The comment data to be created.

    Returns:
        Comment: The newly created comment object.

    Raises:
        HTTPException: If there is an error during the creation process.
    """
    db_comment = Comment(author_id=author_id, photo_id=photo_id, **comment.model_dump())
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

def update_comment(db: Session, comment_id: int, author_id: int, comment: CommentUpdate):
    """Update an existing comment.

    Args:
        db (Session): The database session used for interacting with the database.
        comment_id (int): The ID of the comment to be updated.
        author_id (int): The ID of the user who owns the comment.
        comment (CommentUpdate): The updated comment data.

    Returns:
        Comment: The updated comment object.

    Raises:
        HTTPException: If the comment is not found or if the author does not match.
    """
    db_comment = db.query(Comment).filter(
        Comment.id == comment_id,
        Comment.author_id == author_id
    ).first()
    if not db_comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=COMMENT_NOT_FOUND)
    if comment.content:
        db_comment.content = comment.content
    db.commit()
    db.refresh(db_comment)
    return db_comment

def delete_comment(db: Session, comment_id: int):
    """Delete a comment by its ID.

    Args:
        db (Session): The database session used for interacting with the database.
        comment_id (int): The ID of the comment to be deleted.

    Returns:
        dict: A dictionary containing a success message.

    Raises:
        HTTPException: If the comment is not found.
    """
    db_comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not db_comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=COMMENT_NOT_FOUND)
    db.delete(db_comment)
    db.commit()
    return {"detail": COMMENT_DEL}

def get_comments_by_photo(db: Session, photo_id: int):
    """Retrieve all comments associated with a specific photo.

    Args:
        db (Session): The database session used for interacting with the database.
        photo_id (int): The ID of the photo for which to retrieve comments.

    Returns:
        List[Comment]: A list of comments associated with the specified photo.
    """
    return db.query(Comment).filter(Comment.photo_id == photo_id).all()
