from sqlalchemy import Column, Integer, String, Text, Boolean, DECIMAL, func, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.orm import relationship
from sqlalchemy import Table, Column, ForeignKey

photo_tag_association = Table(
    'photo_tag_association',
    Base.metadata,
    Column('photo_id', ForeignKey('photos.id'), primary_key=True),
    Column('tag_id', ForeignKey('tags.id'), primary_key=True)
)


Base = declarative_base()

class _RoleEnum(Enum):
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
    avatar = Column(String(255), nullable=True)
    rate = Column(Integer)
    role = Column(Enum(_RoleEnum), default=_RoleEnum.user)


class Post(Base):
    """Represents a blog post in the system.

    Attributes:
        id (int): Unique identifier for the post.
        author_id (int): Foreign key referencing the User who created the post.
        img_origin (int): Foreign key referencing the original image associated
            with the post (optional).
        content (str): The content of the post (optional).
        rate (Decimal): The rating of the post (optional).
        is_active (bool): Flag indicating whether the post is active. Default is False.
        created_at (datetime): Timestamp for when the post was created. Automatically set
            to the current time.
        modified (datetime): Timestamp for when the post was last modified. Automatically updated
            to the current time.

    Relationships:
        user (User): The User who authored the post. Establishes a one-to-many relationship
            with the User class.
        images (List[Image]): A list of Image objects associated with the post. Establishes
            a one-to-many relationship with the Image class.

    Example:
        # Creating a new post instance
        new_post = Post(
            author_id=1,
            content="This is a sample blog post.",
            rate=4.5,
            is_active=True
        )
    """
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    author_id = Column(
        ForeignKey('users.id', ondelete='CASCADE'),
        default=None
    )
    img_origin = Column(
        ForeignKey('images.id', ondelete='CASCADE'),
        default=None
    )
    content = Column(Text, nullable=True)
    rate = Column(DECIMAL, nullable=True)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    modified = Column(DateTime, default=func.now(), onupdate=func.now())

    user = relationship('User', backref="posts")
    images = relationship('Image', backref="post")


class Tag(Base):
    """Represents a tag associated with posts in the system.

    Attributes:
        id (int): Unique identifier for the tag.
        name (str): The name of the tag. This field is required and must be unique.

    Example:
        # Creating a new tag instance
        new_tag = Tag(name="Python")
    """
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)


class PostsToTags(Base):
    """Represents the association between posts and tags in the system.

    This class serves as a junction table for establishing a many-to-many
    relationship between the Post and Tag classes, allowing a post to be
    associated with multiple tags and a tag to be linked to multiple posts.

    Attributes:
        post_id (int): Foreign key referencing the ID of the post.
            This field is part of the primary key.
        tag_id (int): Foreign key referencing the ID of the tag.
            This field is part of the primary key.

    Relationships:
        post (Post): The Post associated with this entry in the junction table.
        tag (Tag): The Tag associated with this entry in the junction table.

    Example:
        # Creating an association between a post and a tag
        post_tag_association = PostsToTags(post_id=1, tag_id=2)
    """
    __tablename__ = "posts_to_tags"

    post_id = Column(
        ForeignKey('posts.id', ondelete='CASCADE'),
        primary_key=True
    )
    tag_id = Column(
        ForeignKey('tags.id', ondelete='CASCADE'),
        primary_key=True
    )

    post = relationship('Post', backref="post_tags")
    tag = relationship('Tag', backref="tag_posts")


class Image(Base):
    """Represents an image associated with a post in the system.

    This class stores information about images that can be linked to
    specific posts, allowing for multiple images to be associated
    with a single post.

    Attributes:
        id (int): Unique identifier for the image.
        post_id (int): Foreign key referencing the ID of the associated post (optional).
        link (str): The URL or path to the image file (optional).
        created_at (datetime): Timestamp for when the image was created.
            Automatically set to the current time.

    Relationships:
        post (Post): The Post associated with this image.

    Example:
        # Creating a new image instance linked to a post
        new_image = Image(post_id=1, link="http://example.com/image.jpg")
    """
    __tablename__ = "images"

    id = Column(Integer, primary_key=True)
    post_id = Column(
        ForeignKey('posts.id', ondelete='CASCADE'),
        default=None
    )
    link = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=func.now())

    post = relationship('Post', backref="images")


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
    author_id = Column(
        ForeignKey('users.id', ondelete='CASCADE'),
        default=None
    )
    post_id = Column(
        ForeignKey('posts.id', ondelete='CASCADE'),
        default=None
    )
    content = Column(Text, nullable=True)
    rate = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    modified = Column(DateTime, default=func.now(), onupdate=func.now())

class Photo(Base):
    __tablename__ = 'photos'
    id = Column(Integer, primary_key=True, index=True)
    image_url = Column(String, nullable=False)
    description = Column(String, nullable=True)
    tags = relationship('Tag', secondary=photo_tag_association, back_populates="photos")
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="photos")

class Tag(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    photos = relationship('Photo', secondary=photo_tag_association, back_populates="tags")

    User.photos = relationship('Photo', back_populates='user')  
    author = relationship('User', backref="comments")
    post = relationship('Post', backref="comments")
