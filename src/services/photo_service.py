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

def upload_file(file):
     # Створення унікального імені для файлу
    unique_filename = str(uuid.uuid4()) + pathlib.Path(file.filename).suffix
    # Завантаження файлу на Cloudinary
    try:
        upload_result = cloudinary.uploader.upload(file.file, public_id=unique_filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка завантаження на Cloudinary: {str(e)}")
    return upload_result['url'], upload_result['public_id']

def delete_image(public_id):
    """Видаляє фото вертає True/false """
    response = cloudinary.uploader.destroy(public_id)
    if response["result"] == "ok":
        return True
    return False


def transform_image(public_id):
    """Трансформация изображения"""
    transformed_url = cloudinary.CloudinaryImage(public_id).build_url(transformation=[
        {'width': 500, 'height': 500, 'crop': 'fill'}
    ])
    return transformed_url


# TO DO ->
# def generate_qr_code(link: str):
#     """Генерация QR-кода для ссылки"""
#     img = qrcode.make(link)
#     buffer = BytesIO()
#     img.save(buffer, format="PNG")
#     buffer.seek(0)
#     return buffer
