"""Service to work with Cloudinary"""
import uuid
import pathlib
import qrcode
import cloudinary
import cloudinary.uploader
from fastapi import HTTPException

from src.conf.config import settings


cloudinary_config = cloudinary.config(
    cloud_name = settings.cloudinary_name,
    api_key = settings.cloudinary_api_key,
    api_secret = settings.cloudinary_api_secret,
    secure = settings.cloudinary_secure
)

def upload_file(file) -> tuple[str, str]:
    """Upload a file to Cloudinary and return its URL and public ID.

    This function generates a unique filename, uploads the provided file to Cloudinary,
    and returns the resulting file's URL and public ID. If the upload fails, it raises
    an HTTPException with an error message.

    Args:
        file (UploadFile): The file to be uploaded to Cloudinary.

    Raises:
        HTTPException: Raised if there is an error during the file upload process.

    Returns:
        tuple[str, str]: A tuple containing the file's Cloudinary URL and its public ID.
    """
    unique_filename = str(uuid.uuid4()) + pathlib.Path(file.filename).suffix
    try:
        upload_result = cloudinary.uploader.upload(file.file, public_id=unique_filename)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Помилка завантаження на Cloudinary: {str(e)}"
        ) from e
    return upload_result['url'], upload_result['public_id']

def delete_image(public_id: str) -> bool:
    """Delete an image from Cloudinary.

    This function attempts to delete an image from Cloudinary using the image's public ID.
    If the deletion is successful, it returns `True`; otherwise, it returns `False`.

    Args:
        public_id (str): The Cloudinary public ID of the image to be deleted.

    Returns:
        bool: `True` if the image was successfully deleted, `False` otherwise.
    """
    response = cloudinary.uploader.destroy(public_id)
    if response["result"] == "ok":
        return True
    return False

def crop_and_scale(public_id: str, width: int, height: int) -> str:
    """Crop and scale an image stored on Cloudinary.

    This function takes an image's public ID from Cloudinary and generates a URL
    for the cropped and scaled version of the image. The image is resized to fit
    within the specified width and height while maintaining its aspect ratio by
    cropping any excess.

    Args:
        public_id (str): The Cloudinary public ID of the image to be transformed.
        width (int): The target width of the cropped image.
        height (int): The target height of the cropped image.

    Returns:
        str: The URL of the transformed image in `.jpg` format.
    """
    transformed_image = cloudinary.CloudinaryImage(public_id).build_url(
        width=width,
        height=height,
        crop="fill"
    )
    return transformed_image+".jpg"

#======================= TO DO =========================

# def add_text_overlay(image_public_id, text, font_size=30, color="white"):
#     transformed_image = cloudinary.CloudinaryImage(image_public_id).build_url(
#         overlay={"font_family": "Arial", "font_size": font_size, "text": text, "color": color},
#         gravity="south",
#         crop="scale"
#     )
#     return transformed_image


# def apply_filter(image_public_id, effect="sepia"):
#     transformed_image = cloudinary.CloudinaryImage(image_public_id).build_url(
#         effect=effect
#     )
#     return transformed_image


# def generate_qr_code(link: str):
#     """Генерация QR-кода для ссылки"""
#     img = qrcode.make(link)
#     buffer = BytesIO()
#     img.save(buffer, format="PNG")
#     buffer.seek(0)
#     return buffer
