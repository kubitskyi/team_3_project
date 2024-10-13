from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from typing import List
from sqlalchemy.orm import Session
from src.database.connect import  get_db
from src.database.models import  User, Tag, Photo
from src.schemas.posts import PhotoResponse, PhotoCreate, PhotoUpdate
from src.repository import posts as posts_crud
from src.services.cloudinary import  upload_file
from src.services.auth import auth_service


router = APIRouter(prefix="/posts", tags=["Posts"])


@router.post("/photo", response_model=PhotoCreate)
async def upload_photo(file: UploadFile = File(...),
                       description: str = "No description",
                       db: Session = Depends(get_db),
                       tags: List[str] = [],
                       current_user: User = Depends(auth_service.get_current_user)):
    
    photo_url, public_id = upload_file(file)
    
    tags_list = []
    if len(tags) > 0:
        tags_list = tags[0].split(",")

    if len(tags_list) > 5:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Too many tags. Available only 5 tags.")

    tags = []
    for tag in tags_list:
        new_tag = db.query(Tag).filter(Tag.name==tag).one_or_none()
        if new_tag == None:
            new_tag = Tag(name=tag)
            db.add(new_tag)
            db.commit()
        tags.append(new_tag)
    new_photo = posts_crud.create_photo(db=db, photo_url=photo_url, tags=tags,public_id=public_id, description=description,current_user=current_user)
    return new_photo

    
# , response_model=PhotoResponse
@router.delete("/photo/{photo_id}")
async def delete_photo(photo_id: int, db: Session = Depends(get_db),current_user: User = Depends(auth_service.get_current_user)):
    
    photo = db.query(Photo).filter(Photo.id == photo_id).one_or_none()
    if  auth_service.check_access(user = current_user.id, owner_id=photo.user_id):
        return posts_crud.delete_photo(photo_id, db)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Не авторизовано",
        )
    
    
@router.put("/photo/{photo_id}", response_model=PhotoUpdate)
async def update_photo(photo_id: int,
                       description: str = "No description",
                       db: Session = Depends(get_db),
                       tags: List[str] = [],
                       current_user: User = Depends(auth_service.get_current_user)):
    
    photo = db.query(Photo).filter(Photo.id == photo_id).one_or_none()
    if  auth_service.check_access(user = current_user.id, owner_id=photo.user_id):
        tags_list = []
        if len(tags) > 0:
            tags_list = tags[0].split(",")

        if len(tags_list) > 5:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Too many tags. Available only 5 tags.")
        
        tags = []
        for tag in tags_list:
            new_tag = db.query(Tag).filter(Tag.name==tag).one_or_none()
            if new_tag == None:
                new_tag = Tag(name=tag)
                db.add(new_tag)
                db.commit()
                print("%"*30)
                print(new_tag.id)
            tags.append(new_tag)
        return posts_crud.update_photo(photo_id, description, tags, db)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Не авторизовано",
        )
        
@router.get("/photo/{photo_id}", response_model=PhotoResponse)
async def get_photo(photo_id: int, db: Session = Depends(get_db)):
    return posts_crud.get_photo(photo_id, db)
