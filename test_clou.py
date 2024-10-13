import os
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader

load_dotenv()
cl_name = os.getenv('CLOUDINARY_NAME')
cl_key = os.getenv('CLOUDINARY_API_KEY')
cl_secret = os.getenv('CLOUDINARY_API_SECRET')
cl_secure = os.getenv('CLOUDINARY_SECURE')


cloudinary_config = cloudinary.config( 
  cloud_name = cl_name, 
  api_key = cl_key,
  api_secret = cl_secret,
  secure = cl_secure
)

load_dotenv()
def delete_file(public_id):
    """Видаляє фото вертає True/false """
    response = cloudinary.uploader.destroy(public_id, )
    print(response)
    return True

if __name__ == "__main__":
    print(delete_file("70d752ef-46c7-40f6-9283-16457322ea3b.png"))