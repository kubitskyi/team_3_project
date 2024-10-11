from pydantic import BaseModel
from typing import List
from datetime import datetime

class PhotoResponse(BaseModel):
    id: int
    description: str
    image_url: str
    tags: List[str]
    created_at: datetime
    updated_at: datetime

class PhotoUpload(BaseModel):
    description: str
    image_url: str
    tags: List[str]
    

    class Config:
        from_attributes = True
