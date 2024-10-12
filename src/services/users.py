"""Service file for users operations"""
from fastapi import HTTPException, status

from src.database.models import RoleEnum

def validate_role(role: str) -> str:
    """Validates the provided role against the allowed roles defined in `RoleEnum`.

    Args:
        role (str): The role string to be validated.

    Raises:
        HTTPException: If the provided role is not valid according to `RoleEnum`.

    Returns:
        RoleEnum object: The role that is RoleEnum objecct.
    """
    role.strip().lower()
    try:
        return RoleEnum(role)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="UserServices: Invalid role"
        ) from e
