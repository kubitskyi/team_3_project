import cloudinary
from cloudinary import CloudinaryImage
from src.conf.config import settings
import qrcode

cloudinary.config( 
  cloud_name = settings.cloudinary_name, 
  api_key = settings.cloudinary_api_key,
  api_secret = settings.cloudinary_api_secret,
  secure = settings.cloudinary_secure
)

def upload_image(image_url: str):
 
#   cloudinary.uploader.upload("<url>", public_id="quickstart_butterfly", unique_filename = False, overwrite=True)
#   srcURL = CloudinaryImage("quickstart_butterfly").build_url()
#   print("****2. Upload an image****\nDelivery URL: ", srcURL, "\n")
    
    # with open(image_url, 'rd') as file:
    #     file.read()

    # cloudinary.uploader.upload(file.file, public_id=f'NotesApp/{current_user.username}', overwrite=True)
    # src_url = cloudinary.CloudinaryImage(f'NotesApp/{current_user.username}')\
    #                     .build_url(width=250, height=250, crop='fill', version=r.get('version'))

    # return CloudinaryImage("quickstart_butterfly").build_url()
    pass



def get_url():
    ...
    
def image_transformation():
    ...

def get_qrcode():
    """Create qrcode image from url"""
    ...