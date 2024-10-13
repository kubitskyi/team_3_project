from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class PhotoBase(BaseModel):
    description: str
    image_url: str
    tags: List[str]

    class Config:
        from_attributes = True
    
class PhotoCreate(PhotoBase):
    pass

class PhotoResponse(PhotoBase):
    id: int
    description: str
    image_url: str
    user_id: int
    tags: List[str]
    average_rating: float
    created_at: datetime
    updated_at: datetime

class PhotoUpdate(PhotoBase):
    id: int
