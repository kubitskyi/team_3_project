"""Token operations, password checks, authentifisation checks"""
from typing import Optional
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from src.conf.config import settings
from src.database.connect import get_redis
from src.database.connect import get_db
from src.repository.users import get_user_by_email
from src.database.models import User, RoleEnum


class Auth:
    """Authentication and authorization utility class for handling user password
    verification, token generation, and token decoding in a REST API application.

    This class includes methods to hash passwords, verify passwords, create
    access and refresh JWT tokens, decode tokens to extract user information,
    and authenticate the current user based on the token provided.

    Attributes:
        pwd_context (CryptContext): Password hashing context using bcrypt.
        SECRET_KEY (str): The secret key used for encoding and decoding JWT tokens.
        ALGORITHM (str): The algorithm used for JWT encoding.
        oauth2_scheme (OAuth2PasswordBearer): Dependency to extract the bearer token
            from the request for protected routes.
    """
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = settings.secret_key
    ALGORITHM = settings.algorithm
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


    def verify_password(self, plain_password, hashed_password) -> bool:
        """Verify a plain password against a hashed password.

        Args:
            plain_password (str): The plain text password provided by the user.
            hashed_password (str): The hashed password stored in the database.

        Returns:
            bool: True if the plain password matches the hashed password, False otherwise.
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Hash a plain text password using bcrypt.

        Args:
            password (str): The plain text password to hash.

        Returns:
            str: The hashed version of the password.
        """
        return self.pwd_context.hash(password)


    async def create_access_token(self, data: dict, exp_delta: Optional[float] = None) -> str:
        """Create a new JWT access token.

        Args:
            data (dict): The data to encode in the token (e.g., user's email).
            exp_delta (Optional[float], optional): The expiration time in seconds.
                Defaults to 15 minutes if not provided.

        Returns:
            str: The encoded JWT access token as a string.
        """
        to_encode = data.copy()

        if exp_delta:
            expire = datetime.now(timezone.utc) + timedelta(seconds=exp_delta)
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
            exp_delta = 900

        to_encode.update(
            {
                "iat": datetime.now(timezone.utc),
                "exp": expire,
                "scope": "access_token"
            }
        )
        encoded_access_token = jwt.encode(
            to_encode,
            self.SECRET_KEY,
            algorithm=self.ALGORITHM
        )
        return encoded_access_token, exp_delta


    async def create_refresh_token(self, data: dict, exp_delta: Optional[float] = None) -> str:
        """Create a new JWT refresh token.

        Args:
            data (dict): The data to encode in the token (e.g., user's email).
            exp_delta (Optional[float], optional): The expiration time in seconds.
                Defaults to 7 days if not provided.

        Returns:
            str: The encoded JWT refresh token as a string.
        """
        to_encode = data.copy()

        if exp_delta:
            expire = datetime.now(timezone.utc) + timedelta(seconds=exp_delta)
        else:
            expire = datetime.now(timezone.utc) + timedelta(days=7)

        to_encode.update(
            {
                "iat": datetime.now(timezone.utc),
                "exp": expire,
                "scope": "refresh_token"
            }
        )
        encoded_refresh_token = jwt.encode(
            to_encode,
            self.SECRET_KEY,
            algorithm=self.ALGORITHM
        )
        return encoded_refresh_token


    def create_email_token(self, data: dict) -> str:
        """_summary_

        Args:
            data (dict): _description_

        Returns:
            str: _description_
        """
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=3)

        to_encode.update(
            {
                "iat": datetime.now(timezone.utc),
                "exp": expire
            }
        )
        mail_token = jwt.encode(
            to_encode,
            self.SECRET_KEY,
            algorithm=self.ALGORITHM
        )
        return mail_token


    async def decode_refresh_token(self, refresh_token: str) -> str:
        """Decode a refresh token and extract the user's email.

        Args:
            refresh_token (str): The refresh token to decode.

        Raises:
            HTTPException: If the token scope is invalid or if the token cannot be decoded.

        Returns:
            str: The email of the user extracted from the token.
        """
        try:
            payload = jwt.decode(
                refresh_token,
                self.SECRET_KEY,
                algorithms=[self.ALGORITHM]
            )
            if payload['scope'] == 'refresh_token':
                email = payload['sub']
                return email

            print(
                "AuthServices: token is not refresh_token"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid scope for token'
            )
        except JWTError as e:
            print(f"JWT Error in AuthServices: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='AuthServices: Could not validate credentials'
            ) from e


    async def get_current_user(
        self,
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db),
        redis = Depends(get_redis)
    ) -> User:
        """Retrieve the current authenticated user based on the provided access token.

        Args:
            token (str, optional): The access token extracted from the request.
                Defaults to Depends(oauth2_scheme).
            db (Session, optional): The database session. Defaults to Depends(get_db).

        Raises:
            HTTPException: If the token is invalid, expired, the user cannot be found or is
                not in whitelist (redis base).

        Returns:
            User: The user object associated with the token.
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="AuthServices: Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])

            if payload['scope'] == 'access_token':
                email = payload["sub"]
                if email is None:
                    print("AuthServices: no email")
                    raise credentials_exception
            else:
                print("AuthServices: token is not access_token")
                raise credentials_exception

        except JWTError as e:
            print(f"JWT Error in AuthServices: {e}")
            raise credentials_exception from e
        # Check user in base
        user = await get_user_by_email(email, db)
        if user is None:
            raise credentials_exception
        # Check user in whitelist
        token = await redis.get(f"user_token:{user.id}")
        if token is None:
            raise credentials_exception

        return user


    async def get_email_from_token(self, token: str):
        """Decodes the provided JWT token to extract the user's email address.

        Args:
            token (str): The JWT token containing the email address in its payload.

        Raises:
            HTTPException: If the token is invalid or cannot be decoded, an HTTP 422 Unprocessable
                Entity exception is raised with a message indicating the failure.

        Returns:
            str: The email address extracted from the token.
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email = payload["sub"]
            return email

        except JWTError as e:
            print(f"JWT Error in 'src.auth.auth.get_email_from_token': {e}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="AuthServices: Invalid token for email verification"
            ) from e


    async def check_access(
        self,
        user: User,
        owner_id: int
) -> True:
        """Check if the user has access to a resource.

        This function checks whether a user has access to a resource based on their
        ownership of the resource or their role. A user can access the resource if
        they are the owner or if they have one of the required roles ('moderator' or 'admin').

        Args:
            user (User): The user object, containing user details such as ID and role.
            owner_id (int): The ID of the resource owner.

        Raises:
            HTTPException: If the user is neither the owner of the resource nor
            has one of the required roles, a 403 Forbidden exception is raised.

        Returns:
            True: Returns `True` if the user is the owner or has one of the required roles,
            otherwise raises an exception.
        """
        if user.id != owner_id and user.role not in [RoleEnum.moderator, RoleEnum.admin]:
            raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="AuthServices: Access denied"
        )
        return True


    async def check_admin(
        self,
        user: User,
        allowed_roles: list|None = None
    ) -> True:
        """Checks if the user has one of the allowed roles.

        This asynchronous function checks the user's role. If the user's role
        is not in the list of allowed roles, an HTTPException with a 403 status code is raised.

        Args:
            user (User): The user object whose role needs to be checked.
            allowed_roles: optional list of roles.

        Raises:
            HTTPException: If the user's role is not in the allowed roles,
            a 403 Forbidden error is raised with the message "Access denied".

        Returns:
            True: Returns True if the user has one of the allowed roles.
        """
        if not allowed_roles:
            allowed_roles = [RoleEnum.moderator, RoleEnum.admin]
        if user.role not in allowed_roles:
            raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="AuthServices: Access denied"
        )
        return True


#  Import this to make all routers use one instanse of class
auth_service = Auth()
