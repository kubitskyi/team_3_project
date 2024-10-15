"""Schemas for comments"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class CommentBase(BaseModel):
    """Base model for a comment.

    This model defines the common fields that are used in creating and displaying comments,
    such as the comment content.

    Args:
        BaseModel (Pydantic BaseModel): The base model class provided by Pydantic.
    """
    content: str = Field(max_length=500)


class CommentCreate(CommentBase):
    """Model for creating a new comment.

    Inherits all fields from the `CommentBase` model. Used when a user creates a new comment.

    Args:
        CommentBase (Pydantic BaseModel): Inherits from `CommentBase` with no additional fields.
    """
    pass


class CommentUpdate(BaseModel):
    """Model for updating an existing comment.

    This model is used when updating a comment. It allows partial updates by making the
    `content` field optional.

    Args:
        BaseModel (Pydantic BaseModel): The base model class provided by Pydantic.
    """
    content: Optional[str] = Field(None, max_length=500)


class CommentResponse(CommentBase):
    """Response model for a comment.

    This model defines the fields that are returned when a comment is retrieved, including
    metadata such as the comment's ID, the author ID, and timestamps for when the comment
    was created and last updated.

    Args:
        CommentBase (Pydantic BaseModel): Inherits from `CommentBase` to include the comment content.
    """
    id: int
    author_id: int
    photo_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic configuration.

        This configuration setting ensures that the model can be populated from ORM objects,
        allowing the model to interact with database records easily.
        """
        from_attributes = True
