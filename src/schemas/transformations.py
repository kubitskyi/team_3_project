from pydantic import BaseModel, Field
from datetime import datetime


class CropAndScaleRequest(BaseModel):
    """Request model for cropping and scaling a photo.

    This model contains the fields required to request a crop and scale transformation for
    an image. It includes the ID of the photo to be transformed and the target width and
    height in pixels.

    Args:
        BaseModel (Pydantic BaseModel): The base model class provided by Pydantic.

    Attributes:
        photo_id (int): The identifier of the image in Cloudinary to be transformed.
        width (int): The target width of the transformed image, must be greater than 0.
        height (int): The target height of the transformed image, must be greater than 0.
    """
    photo_id: int = Field(..., description="Ідентифікатор публікації зображення в Cloudinary.")
    width: int = Field(..., gt=0, description="Ширина зображення в пікселях.")
    height: int = Field(..., gt=0, description="Висота зображення в пікселях.")

    class Config:
        """Pydantic configuration for extra options.

        The `json_schema_extra` provides an example of the data that might be sent to
        perform a crop and scale request.
        """
        json_schema_extra = {
            "example": {
                "photo_id": "photo_id",
                "width": 800,
                "height": 600
            }
        }


class PhotoTransformationResponse(BaseModel):
    """Response model for photo transformations.

    This model is returned when a photo undergoes a transformation, such as cropping or scaling.
    It includes details about the transformed image, such as the transformation type, the URL of
    the resulting image, and timestamps.

    Args:
        BaseModel (Pydantic BaseModel): The base model class provided by Pydantic.

    Attributes:
        id (int): The unique identifier of the transformed image record.
        original_photo_id (int): The ID of the original photo before transformation.
        transformation_type (str): The type of transformation applied (e.g., "crop_and_scale").
        image_url (str): The URL of the transformed image.
        created_at (datetime): The timestamp when the transformation was applied.
    """
    id: int
    original_photo_id: int
    transformation_type: str
    image_url: str
    created_at: datetime

    class Config:
        """Pydantic configuration.

        This configuration setting ensures that the model can be populated from ORM objects,
        allowing the model to interact with database records easily.
        """
        from_attributes = True
