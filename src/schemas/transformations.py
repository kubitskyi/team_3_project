from pydantic import BaseModel, Field

class CropAndScaleRequest(BaseModel):
    photo_id: int = Field(..., description="Ідентифікатор публікації зображення в Cloudinary.")
    width: int = Field(..., gt=0, description="Ширина зображення в пікселях.")
    height: int = Field(..., gt=0, description="Висота зображення в пікселях.")

    class Config:
        schema_extra = {
            "example": {
                "photo_id": "photo_id",
                "width": 800,
                "height": 600
            }
        }
