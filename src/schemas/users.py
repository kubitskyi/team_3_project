"""Schemas for check"""
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr


class UserCreate(BaseModel):
    """Represents the schema for creating a new user.

    This schema is used for validating user input during signup.

    Args:
        BaseModel (Pydantic BaseModel): The base class for creating data models.

    Attributes:
        username (str): The username of the user, with a minimum length of 5 and
            a maximum length of 20 characters.
        email (EmailStr): The user's email address, validated as a proper email format.
        password (str): The user's password, with a minimum length of 8 and
            a maximum length of 25 characters.
    """
    name: str = Field(min_length=4, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=25)


class UserReturn(BaseModel):
    """Represents the database model for a user, used for returning user data from the database.

    Args:
        BaseModel (Pydantic BaseModel): The base class for creating data models.

    Attributes:
        id (int): The unique identifier of the user.
        username (str): The username of the user.
        email (EmailStr): The email address of the user.
        created_at (datetime): The datetime when the user was created.

    Config:
        from_attributes (bool): Allows Pydantic to convert non-dict objects
            (like SQLAlchemy models) to JSON.
    """
    id: int
    name: str
    email: EmailStr
    created_at: datetime
    modified: datetime
    is_online: bool
    avatar: str | None
    rate: int
    role: str

    class Config:
        """Tells pydantic to convert even non-dict objects to json."""
        from_attributes = True


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
