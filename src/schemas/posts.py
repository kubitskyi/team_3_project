"""Schemas for posts"""
from typing import List
from datetime import datetime
from pydantic import BaseModel


class PhotoBase(BaseModel):
    """Base model for a photo.

    This model contains the common fields shared across photo-related models, such as
    the photo's description, its URL, and associated tags.

    Args:
        BaseModel (Pydantic BaseModel): The base model class provided by Pydantic.
    """
    description: str
    image_url: str
    tags: List[str]

    class Config:
        """Pydantic configuration.

        This configuration setting ensures that the model can be populated from ORM objects,
        allowing the model to interact with database records easily.
        """
        from_attributes = True


class PhotoCreate(PhotoBase):
    """Model for creating a new photo.

    Inherits from `PhotoBase` and is used when a new photo is uploaded.

    Args:
        PhotoBase (Pydantic BaseModel): Inherits all fields from `PhotoBase`.
    """


class PhotoResponse(PhotoBase):
    """Response model for retrieving photo details.

    This model extends the base photo model with additional fields such as the photo's
    ID, the user who uploaded the photo, and timestamps. It is used to return detailed
    information about a photo in API responses.

    Args:
        PhotoBase (Pydantic BaseModel): Inherits fields from `PhotoBase`.
    """
    id: int
    description: str
    image_url: str
    user_id: int
    tags: List[str]
    average_rating: float
    created_at: datetime
    updated_at: datetime

class PhotoUpdate(PhotoBase):
    """Model for updating an existing photo.

    This model is used when updating an existing photo record. It inherits from `PhotoBase`
    and requires the `id` of the photo to be updated.

    Args:
        PhotoBase (Pydantic BaseModel): Inherits fields from `PhotoBase`.
    """
    id: int
