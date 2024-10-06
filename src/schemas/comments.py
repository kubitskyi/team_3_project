from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CommentBase(BaseModel):
    content: str = Field(max_length=500)
    rate: Optional[int] = Field(None, ge=1, le=10)


class CommentCreate(CommentBase):
    pass


class CommentUpdate(BaseModel):
    content: Optional[str] = Field(None, max_length=500)


class CommentResponse(CommentBase):
    id: int
    author_id: int
    post_id: int
    created_at: datetime
    modified: datetime

    class Config:
        orm_mode = True
