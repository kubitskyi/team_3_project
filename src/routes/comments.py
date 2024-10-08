from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from src.database.models import User
from src.schemas.comments import CommentCreate, CommentUpdate, CommentResponse, RateComment
from src.repository.comments import create_comment, update_comment, delete_comment, get_comments_by_photo, rate_comment
from src.database.connect import get_db
from src.services.auth import auth_service as auth_s


router = APIRouter(prefix="/comments", tags=["comments"])


@router.post("/", response_model=CommentResponse)
def create_new_comment(
    photo_id: int,
    comment: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_s.get_current_user)
):
    return create_comment(db, author_id=current_user.id, photo_id=photo_id, comment=comment)


@router.put("/{comment_id}", response_model=CommentResponse)
def update_existing_comment(
    comment_id: int,
    comment: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_s.get_current_user)
):
    return update_comment(db, comment_id=comment_id, author_id=current_user.id, comment=comment)


@router.delete("/{comment_id}", response_model=dict)
def delete_existing_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_s.get_current_user)
):
    if current_user.role not in ["admin", "moderator"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You must be admin or moder for delete this") 
    return delete_comment(db, comment_id=comment_id)


@router.get("/post/{photo_id}", response_model=List[CommentResponse])
def get_comments_for_photo(photo_id: int, db: Session = Depends(get_db)):
    return get_comments_by_photo(db, photo_id=photo_id)


@router.put("/{comment_id}/rate", response_model=RateComment)
def rate_existing_comment(
    comment_id: int,
    rate: RateComment,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_s.get_current_user)
):
    if not current_user:
         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not our user")

    if not (1 <= rate.rate <= 10):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Rate must be between 1 and 10")
    return rate_comment(db, comment_id=comment_id, rate=rate)