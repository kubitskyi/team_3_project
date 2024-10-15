"""Router for authentification"""
from sqlalchemy.orm import Session
from fastapi_limiter.depends import RateLimiter
from fastapi import APIRouter, HTTPException, Depends, status, Security, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer

from src.database.connect import get_db, get_redis
from src.database.models import User
from src.services.mail import send_email
from src.services.auth import auth_service as auth_s
from src.schemas.users import UserCreate, UserCreationResp, TokenModel, RequestEmail
from src.repository.users import (
    get_user_by_email, create_user, update_token, confirmed_check_toggle
)


router = APIRouter(prefix='/auth', tags=["Authentification"])
get_refr_token = HTTPBearer()


@router.post(
    "/signup",
    response_model=UserCreationResp,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RateLimiter(times=5, seconds=30))]
)
async def signup(
    body: UserCreate,
    bt: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db)
) -> dict:
    """## Handles user registration by creating a new user account.
    ```
    /api/auth/signup
    ```
    This endpoint allows a new user to register by providing their name, email, and password.
    The password is hashed before being stored in the database. If the email is already in use,
    an HTTP 409 Conflict error is raised.

    ### Args:
        body (UserScema): The request body containing the new user's data, including
            name, email, and password.
        db (Session, optional): The database session dependency, automatically injected by FastAPI.

    ### Raises:
        HTTPException: If the email provided is already associated with an existing account,
            a 409 Conflict error is raised with the message "Account already exists".

    ### Returns:
        dict: A dictionary containing the newly created user's data and a success message.
            The dictionary includes:
            - "user": The `UserReturn` model instance representing the new user.
            - "detail": A message indicating the user was successfully created.
    """
    user_ = await get_user_by_email(body.email, db)
    if user_:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="UserRouter: Account already exists"
        )
    body.password = auth_s.get_password_hash(body.password)
    new_user = await create_user(body, db)
    bt.add_task(send_email, new_user.email, new_user.name, str(request.base_url))
    return {
        "user": new_user,
        "detail": "User successfully created. Check your email for confirmation."
    }

@router.post(
    "/login",
    response_model=TokenModel,
    dependencies=[Depends(RateLimiter(times=10, seconds=300))]
)
async def login(
    body: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    redis = Depends(get_redis)
) -> TokenModel:
    """## Authenticates a user and generates access and refresh tokens.
    ```
    /api/auth/login
    ```
    This endpoint allows a registered user to log in by providing their email (as name)
    and password. If the credentials are correct, it returns a pair of JWT tokens:
    an access token and a refresh token. If the credentials are incorrect, an appropriate
    HTTP error is raised.

    ### Args:
        body (OAuth2PasswordRequestForm, optional): The login form data containing the name
        (email) and password. This is automatically populated by FastAPI using dependency injection.
        db (Session, optional): The database session dependency, automatically injected by FastAPI.

    ### Raises:
        HTTPException: If the user does not exist, a 404 Not Found error is raised
            with the message "Invalid data".
        HTTPException: If the password is incorrect, a 401 Unauthorized error is raised
            with the message "Invalid data".

    ### Returns:
        TokenModel: An object containing the access token, refresh token,
            and the token type (bearer).
    """
    user = await get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="UserRouter: Invalid data"
        )
    if not auth_s.verify_password(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="UserRouter: Invalid data"
        )
    if user.is_active is False:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="UserRouter: User is not confirmed"
        )
    if user.banned:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="UserRouter: User is banned."
        )
    access_token_, exp = await auth_s.create_access_token(data={"sub": user.email})
    refresh_token_ = await auth_s.create_refresh_token(data={"sub": user.email})
    await redis.set(f"user_token:{user.id}", access_token_, ex=exp)
    await update_token(user, refresh_token_, db)
    return {
        "access_token": access_token_,
        "refresh_token": refresh_token_,
        "token_type": "bearer"
    }

@router.post("/logout", response_model=dict)
async def logout(
    current_user: User = Depends(auth_s.get_current_user),
    db: Session = Depends(get_db),
    redis = Depends(get_redis)
) -> dict:
    """## Logs out the current authenticated user.
    ```
    /api/auth/logout
    ```
    This endpoint allows the user to log out by removing their access token
    from the Redis cache, effectively invalidating it.

    ### Args:
        current_user (User, optional): The current authenticated user.
            Injected via `Depends(auth_s.get_current_user)`.
        db (Session, optional): The database session dependency. Injected via `Depends(get_db)`.

    ### Returns:
        dict: A message indicating that the user has successfully logged out.
    """
    await redis.delete(f"user_token:{current_user.id}")
    await update_token(current_user, None, db)
    return {"message": "Successfully logged out."}

@router.get(
    '/refresh_token',
    response_model=TokenModel,
    dependencies=[Depends(RateLimiter(times=5, seconds=30))]
)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Security(get_refr_token),
    db: Session = Depends(get_db),
    redis = Depends(get_redis)
) -> TokenModel:
    """## Refreshes the JWT access and refresh tokens for a user.
    ```
    /api/auth/refresh_token
    ```
    This endpoint allows a user to obtain a new pair of access and refresh tokens using
    a valid refresh token. It validates the provided refresh token, ensures it matches the one
    stored in the database, and then generates new tokens. If the refresh token is invalid or
    does not match, an error is raised.

    ### Args:
        credentials (HTTPAuthorizationCredentials, optional): The credentials object containing
            the refresh token. This is automatically provided via dependency injection using
            the `Security` dependency with `get_refr_token`.
        db (Session, optional): The database session dependency, automatically injected by FastAPI.

    ### Raises:
        HTTPException: If the refresh token is invalid or does not match the one stored in
            the user's record, a 401 Unauthorized error is raised with
            the message "Invalid refresh token".

    ### Returns:
        TokenModel: An object containing the new access token, refresh token, a
            nd the token type (bearer).
    """
    token = credentials.credentials
    email = await auth_s.decode_refresh_token(token)
    user = await get_user_by_email(email, db)
    if user.refresh_token != token:
        await update_token(user, None, db)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="UserRouter: Invalid refresh token"
        )
    access_token_, exp = await auth_s.create_access_token(data={"sub": email})
    refresh_token_ = await auth_s.create_refresh_token(data={"sub": email})
    await redis.set(f"user_token:{user.id}", access_token_, ex=exp)
    await update_token(user, refresh_token_, db)
    return {
        "access_token": access_token_,
        "refresh_token": refresh_token_,
        "token_type": "bearer"
    }

@router.get(
    '/confirmed_email/{token}',
    dependencies=[Depends(RateLimiter(times=5, seconds=30))]
)
async def confirmed_email(token: str, db: Session = Depends(get_db)) -> dict:
    """## Confirm a user's email based on the provided token.
    ```
    /api/auth/confirmed_email/_token_
    ```
    This endpoint validates the email confirmation token, checks if the user's email is
    already confirmed, and updates the confirmation status if necessary. It is rate-limited
    to 5 requests every 30 seconds to prevent abuse.

    ### Args:
        token (str): The email confirmation token.
        db (Session, optional): The database session dependency. Defaults to Depends(get_db).

    ### Raises:
        HTTPException: Raised with a 400 status code if the user is not found or if the token
            is invalid.

    ### Returns:
        dict: A dictionary containing a confirmation message. The message is either:
            - "Email confirmed" if the confirmation was successful.
            - "Your email is already confirmed" if the email was previously confirmed.
    """
    email = await auth_s.get_email_from_token(token)
    user = await get_user_by_email(email, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="UserRouter: Verification error"
        )
    if user.is_active:
        return {"message": "UserRouter: Your email is already confirmed"}
    await confirmed_check_toggle(email, db)
    return {"message": "App: Email confirmed"}

@router.post(
    '/request_email',
    dependencies=[Depends(RateLimiter(times=5, seconds=30))]
)
async def request_email(
    body: RequestEmail,
    bt: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db)
) -> dict:
    """## Request email to repeat confirmation for a user.
    ```
    /api/auth/request_email
    ```
    This endpoint allows users to request a confirmation email if their email is not yet confirmed.
    If the email is already confirmed, it informs the user. The confirmation email is sent
    asynchronously using background tasks. The function is rate-limited to 5 requests every
    30 seconds.

    ### Args:
        body (RequestEmail): The request body containing the user's email address.
        bt (BackgroundTasks): A background task manager for sending the email asynchronously.
        request (Request): The HTTP request object, used to get the base URL.
        db (Session, optional): The database session dependency. Defaults to Depends(get_db).

    ### Returns:
        dict: A dictionary containing a message. The message is either:
            - "Your email is already confirmed" if the email was previously confirmed.
            - "Check your email for confirmation." if the confirmation email was successfully
                requested.
    """
    user = await get_user_by_email(body.email, db)
    if user.is_active:
        return {"message": "Your email is already confirmed"}
    if user:
        bt.add_task(send_email, user.email, user.name, str(request.base_url))
    return {"message": "Check your email for confirmation."}
