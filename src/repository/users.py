"""CRUD operations"""
from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas.users import UserCreate


async def get_user_by_email(email: str, db: Session) -> User:
    """Retrieve a user from the database by their email address.

    Args:
        email (str): The email address of the user to retrieve.
        db (Session): The database session used for querying the user.

    Returns:
        User: The user object if found, otherwise None.
    """
    return db.query(User).filter(User.email == email).first()


async def get_user_by_name(name: str, db: Session) -> User:
    """Retrieve a user from the database by their name.

    Args:
        name (str): The name of the user to retrieve.
        db (Session): The database session used for querying the user.

    Returns:
        User: The user object if found, otherwise None.
    """
    return db.query(User).filter(User.name == name).first()


async def create_user(body: UserCreate, db: Session) -> User:
    """Create a new user in the database.

    Args:
        body (UserScema): The schema containing user information such as email, password, etc.
        db (Session): The database session used to add the new user.

    Returns:
        User: The newly created user object.
    """
    new_user = User(**body.model_dump())
    # Check if this is first user
    check = db.query(User).count()
    if not check:
        new_user.role = "admin"

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


async def update_token(user: User, token: str | None, db: Session) -> None:
    """Update the refresh token of a user in the database.

    Args:
        user (User): The user object whose refresh token needs to be updated.
        token (str | None): The new refresh token to set for the user. Pass None to clear the token.
        db (Session): The database session used to update the user's token.
    """
    user.refresh_token = token
    db.commit()

async def confirmed_check_toggle(email: str, db: Session) -> None:
    """Toggle the email confirmation status of a user.

    This function retrieves a user by their email and marks their account as confirmed by
    setting the `confirmed` attribute to `True`. The changes are then committed to the database.

    Args:
        email (str): The email of the user whose confirmation status will be toggled.
        db (Session): The database session used to retrieve and update the user's record.

    Returns:
        None
    """
    user = await get_user_by_email(email, db)
    user.is_active = True
    db.commit()

async def update_avatar(email, url: str, db: Session) -> User:
    """Update the avatar URL for a specific user.

    This function retrieves a user by their email, updates their avatar URL,
    and commits the change to the database.

    Args:
        email (str): The email of the user whose avatar is being updated.
        url (str): The new avatar URL to be saved to the user's profile.
        db (Session): The database session used to retrieve and update the user.

    Returns:
        User: The updated user object with the new avatar URL.
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user

async def delete_avatar(user: User, db: Session) -> None:
    user.avatar = None
    db.commit()

async def ban_offender(user: User, db: Session) -> None:
    user.banned = True
    db.commit()
