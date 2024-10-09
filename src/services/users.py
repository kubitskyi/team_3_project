from fastapi import HTTPException, status

from src.database.models import RoleEnum

def check_role(role: str) -> str:
    """Validates the provided role against the allowed roles defined in `RoleEnum`.

    Args:
        role (str): The role string to be validated.

    Raises:
        HTTPException: If the provided role is not valid according to `RoleEnum`.

    Returns:
        str: The sanitized and validated role string.
    """
    role.strip().lower()
    allowed_roles = [r.value for r in RoleEnum]
    if role not in allowed_roles:
        raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="AuthServices: Invalid role"
            )
    return role
