from pydantic import BaseModel, Field, conint
from typing import Optional
from datetime import datetime


class CommentBase(BaseModel):
    content: str = Field(max_length=500)


class CommentCreate(CommentBase):
    pass


class CommentUpdate(BaseModel):
    content: Optional[str] = Field(None, max_length=500)


class CommentResponse(CommentBase):
    id: int
    author_id: int
    photo_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
