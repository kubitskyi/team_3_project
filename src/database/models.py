"""Models"""
from enum import Enum
from sqlalchemy import Table, Column, Integer, String, Text, Boolean, DateTime, func, JSON, Float
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.orm import relationship


Base = declarative_base()


photo_tag_association = Table(
    'photo_tag_association',
    Base.metadata,
    Column('photo_id', ForeignKey('photos.id',ondelete='CASCADE'), primary_key=True),
    Column('tag_id', ForeignKey('tags.id',ondelete='CASCADE'), primary_key=True)
)


class RoleEnum(Enum):
    """Roles for user"""
    user = "user"
    admin = "admin"
    moderator = "moderator"


class User(Base):
    """Represents a user in the system.

    Attributes:
        id: Unique identifier for the user.
        name: User's name (unique).
        email: User's email address (unique).
        password: User's password (hashed).
        created_at: Timestamp for when the user was created.
        modified: Timestamp for when the user was last modified.
        refresh_token: Token for refreshing sessions.
        is_active: Flag indicating if the user account is active.
        is_online: Flag indicating if the user is currently online.
        avatar: URL or path to the user's avatar.
        rate: User's rating (optional).
        role: User's role in the system (user, admin, etc.).
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=func.now())
    modified = Column(DateTime, default=func.now(), onupdate=func.now())
    refresh_token = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=False)
    is_online = Column(Boolean, default=False)
    banned = Column(Boolean, default=False)
    avatar = Column(String(255), nullable=True)
    photo_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    role = Column(SQLAlchemyEnum(RoleEnum), default=RoleEnum.user)
    about = Column(Text, nullable=True, default=None)
    photos = relationship("Photo", back_populates="user")
    photo_ratings = relationship('PhotoRating', back_populates='user')


class Photo(Base):
    __tablename__ = 'photos'
    id = Column(Integer, primary_key=True, index=True)
    image_url = Column(String, nullable=False)
    description = Column(String, nullable=True)
    public_id = Column(String, nullable=True)
    user_id = Column(ForeignKey('users.id', ondelete='CASCADE'),default=None)
    user = relationship("User", back_populates="photos")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now(), nullable=True)
    # Теги
    tags = relationship('Tag', secondary=photo_tag_association, back_populates="photos")
    # Рейтинг
    average_rating = Column(Float, default=0)
    ratings = relationship('PhotoRating', back_populates='photo', cascade="all, delete")
    # Відношення для трансформацій
    transformations = relationship('PhotoTransformation', back_populates='photo', cascade="all, delete")


class Tag(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    photos = relationship('Photo', secondary=photo_tag_association, back_populates="tags")


class Comment(Base):
    """Represents a comment made by a user on a post.

    This class stores information about comments, including the author,
    content, and associated post. Comments allow users to interact with
    posts by providing feedback or discussions.

    Attributes:
        id (int): Unique identifier for the comment.
        author_id (int): Foreign key referencing the User who made the comment.
        post_id (int): Foreign key referencing the Post that this comment is associated with.
        content (str): The text content of the comment (optional).
        rate (int): Rating given to the comment (optional).
        is_active (bool): Flag indicating whether the comment is active. Default is False.
        created_at (datetime): Timestamp for when the comment was created. Automatically set
            to the current time.
        modified (datetime): Timestamp for when the comment was last modified. Automatically
            updated to the current time.

    Relationships:
        author (User): The User who authored the comment.
        post (Post): The Post associated with this comment.

    Example:
        # Creating a new comment instance
        new_comment = Comment(author_id=1, post_id=2, content="Great post!", rate=5)
    """
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True)
    author_id = Column(ForeignKey('users.id', ondelete='CASCADE'), default=None)
    photo_id = Column(ForeignKey('photos.id', ondelete='CASCADE'), default=None)
    content = Column(Text, nullable=True)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class PhotoRating(Base):
    __tablename__ = 'photo_ratings'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    photo_id = Column(Integer, ForeignKey('photos.id'), primary_key=True)
    rating = Column(Integer, nullable=False)  # Рейтинг від 1 до 5
    user = relationship('User', back_populates='photo_ratings')
    photo = relationship('Photo', back_populates='ratings')

    
class PhotoTransformation(Base):
    __tablename__ = 'photo_transformations'
    
    id = Column(Integer, primary_key=True, index=True)
    original_photo_id = Column(ForeignKey('photos.id', ondelete='CASCADE'))
    photo = relationship('Photo', back_populates='transformations')
    transformation_type = Column(String, nullable=False)  
    # Силки
    image_url = Column(String, nullable=False) 
    created_at = Column(DateTime, server_default=func.now())
