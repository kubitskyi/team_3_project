from sqlalchemy.orm import Session
from database.models import Comment
from schemas.comments import CommentCreate, CommentUpdate, CommentResponse, CommentBase
from fastapi import HTTPException, status


def create_comment(db: Session, author_id: int, post_id: int, comment: CommentCreate):
    db_comment = Comment(author_id=author_id, post_id=post_id, **comment.dict())
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


def update_comment(db: Session, comment_id: int, author_id: int, comment: CommentUpdate):
    db_comment = db.query(Comment).filter(Comment.id == comment_id, Comment.author_id == author_id).first()
    if not db_comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    
    if comment.content:
        db_comment.content = comment.content

    db.commit()
    db.refresh(db_comment)
    return db_comment


def delete_comment(db: Session, comment_id: int):
    db_comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not db_comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    db.delete(db_comment)
    db.commit()
    return {"detail": "Comment deleted successfully"}


def get_comments_by_post(db: Session, post_id: int):
    return db.query(Comment).filter(Comment.post_id == post_id).all()


def rate_comment(db: Session, comment_id: int, rate: int):
    db_comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not db_comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    
    db_comment.rate = rate
    db.commit()
    db.refresh(db_comment)
    return db_comment
