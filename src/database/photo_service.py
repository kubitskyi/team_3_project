import cloudinary
import cloudinary.uploader
import qrcode
from io import BytesIO
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"  # Используем SQLite для тестов

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

cloudinary.config(
    cloud_name="your_cloud_name",
    api_key="your_api_key",
    api_secret="your_api_secret"
)

def upload_image_to_cloudinary(file):
    """Загрузка изображения в Cloudinary"""
    result = cloudinary.uploader.upload(file)
    return result['url'], result['public_id']

def transform_image(public_id):
    """Трансформация изображения"""
    transformed_url = cloudinary.CloudinaryImage(public_id).build_url(transformation=[
        {'width': 500, 'height': 500, 'crop': 'fill'}
    ])
    return transformed_url

def generate_qr_code(link: str):
    """Генерация QR-кода для ссылки"""
    img = qrcode.make(link)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer
