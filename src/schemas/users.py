"""Schemas for check"""
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr


class UserCreate(BaseModel):
    """Represents the schema for creating a new user.

    This schema is used for validating user input during signup.

    Args:
        BaseModel (Pydantic BaseModel): The base class for creating data models.

    Attributes:
        name (str): The username of the user, with a minimum length of 5 and
            a maximum length of 20 characters.
        email (EmailStr): The user's email address, validated as a proper email format.
        password (str): The user's password, with a minimum length of 8 and
            a maximum length of 25 characters.
    """
    name: str = Field(min_length=4, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=25)


class UserPublic(BaseModel):
    """Public model for user data.

    This model represents the publicly visible information of a user, including their
    name, account creation date, online status, and other user-related statistics. This
    model is useful for displaying user profiles or public user data in the system.

    Args:
        BaseModel (Pydantic BaseModel): The base model class provided by Pydantic.

    Attributes:
        name (str): The user's display name.
        created_at (datetime): The date and time when the user's account was created.
        is_online (bool): Indicates whether the user is currently online.
        avatar (str | None): The URL of the user's avatar image, or None if not set.
        photo_count (int): The total number of photos uploaded by the user.
        comment_count (int): The total number of comments made by the user.
        role (str): The user's role in the system (e.g., "user", "admin").
        about (str | None): A brief description or bio provided by the user, or None if not set.
    """
    name: str
    created_at: datetime
    is_online: bool
    avatar: str | None
    photo_count: int
    comment_count: int
    role: str
    about: str | None

    class Config:
        """Pydantic configuration.

        This configuration setting ensures that the model can be populated from ORM objects,
        allowing the model to interact with database records easily.
        """
        from_attributes = True


class UserReturn(UserPublic):
    """Represents the database model for a user, used for returning user data from the database.

    Args:
        BaseModel (Pydantic BaseModel): The base class for creating data models.

    Attributes:
        id (int): The unique identifier of the user.
        email (EmailStr): The email address of the user.
        created_at (datetime): The datetime when the user was created.

    Config:
        from_attributes (bool): Allows Pydantic to convert non-dict objects
            (like SQLAlchemy models) to JSON.
    """
    id: int
    email: EmailStr
    modified: datetime



class UserCreationResp(BaseModel):
    """Represents the response model for user-related operations.

    This schema is used for sending responses when a user is successfully created.

    Args:
        BaseModel (Pydantic BaseModel): The base class for creating data models.

    Attributes:
        user (UserDb): The user data returned as part of the response.
        detail (str): A message indicating the success of the operation.
            Defaults to "User was successfully created".
    """
    user: UserReturn
    detail: str = "User was successfully created"


class TokenModel(BaseModel):
    """Represents the model for authentication tokens.

    This schema is used for returning access and refresh tokens upon successful login
    or token refresh.

    Args:
        BaseModel (Pydantic BaseModel): The base class for creating data models.

    Attributes:
        access_token (str): The JWT access token used for authentication.
        refresh_token (str): The JWT refresh token used to obtain new access tokens.
        token_type (str): The type of the token, which is "bearer" by default.
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    """Request model for email-related actions.

    This model is used to validate and structure the data for an email request,
    typically for requesting email confirmation or password resets.

    Args:
        BaseModel (pydantic.BaseModel): The base class for all Pydantic models.

    Attributes:
        email (EmailStr): The user's email address, validated to ensure it's a proper email format.
    """
    email: EmailStr
