from sqlalchemy.orm import Session
from src.database.models import  Tag


def create_tag(tag_name: str, db: Session):
    tag = db.query(Tag).filter(Tag.name == tag_name).first()
    if tag:
        return tag
    new_tag = Tag(name=tag_name)
    db.add(new_tag)
    db.commit()
    db.refresh()
    return new_tag