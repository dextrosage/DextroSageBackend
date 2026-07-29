from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Path, Request, logger, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from Request_and_Response.Requests import AddOwnProfileRequest, LoginRequest, PasswordReplaceRequest, PhoneNumberVerify, SignUpRequest
from Request_and_Response.Responses import (
    AddOwnProfileResponse,
    LogOutResponse,
    LoginResponse,
    RefreshResponse,
    SignUpResponse,
    UserCredentialsResponse,
)

from auth_jwt.create_tokens import TokenUser, create_access_token, refresh_token
from celery_worker.tasks import send_email, send_email_smtp
from mongodb.db_functions.auth import (
    LoginResult,
    UserDetails,
    UserCredentials,
    add_phone_number,
    clear_refresh_token,
    create_user,
    get_user_credentials,
    replace_password,
    save_refresh_token,
    update_new_refresh_token,
    verify_login_user,
    verify_stored_refresh_token,
)
from dependency.token_dependency import security, verify_admin_access_token, verify_refresh_token, verify_user_access_token
from mongodb.db_functions.user import add_user_profile
from redis_db.limit import check_login_rate_limit, clear_login_limit, get_login_key, record_failed_login
from security.google_sheet import GoogleSheetError, add_user_to_sheet, update_password_in_sheet


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.get("/week5")
def start() -> dict[str, str]:
    return {"status": "From week 5"}


@router.post(
    "/signup",
    response_model=SignUpResponse,
    status_code=status.HTTP_201_CREATED,
)
async def signup(
    signup_cred: SignUpRequest,
    email_send_task: BackgroundTasks,
    payload: dict = Depends(verify_admin_access_token)
) -> dict[str, str]:
    """Register a new user with a unique username."""

    user_created: UserDetails = await create_user(
        signup_cred
    )

    # Storing creds in google sheet
    try:

        await add_user_to_sheet(
            user_id=user_created.user_id,
            username=user_created.username,
            password=user_created.password,
            email=signup_cred.email,
        )

    except GoogleSheetError:

        logger.exception(
            "Unable to save user to Google Sheet."
        )

    # Sending email by SMTP in worker
    email_send_task.add_task(send_email_smtp, signup_cred.name, signup_cred.email, user_created.username,
                             user_created.password)
    # send_email.delay(signup_cred.name, signup_cred.email, user_created.username,
    #                  user_created.password)

    return {
        "status": "Entry successful",
        "email": signup_cred.email
    }


@router.post("/login", response_model=LoginResponse)
async def login(
    login_cred: LoginRequest,
    request: Request
) -> dict[str, str]:
    """Authenticate a user and issue a fresh access/refresh token pair."""

    # Getting redis key
    key = get_login_key(login_cred.username, request)

# 1. Check whether the user is already blocked
    await check_login_rate_limit(key)

    login_result: LoginResult = await verify_login_user(
        login_cred.username,
        login_cred.password
    )

    if not login_result.success:

        await record_failed_login(key)

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # clearing the rate limit on successful login
    await clear_login_limit(key)

    token_user = TokenUser(
        user_id=login_result.user_id,
        session_id=login_result.session_id,
    )
    access_token = create_access_token(token_user)
    refresh_token_value = refresh_token(token_user)

    # Store only a refresh-token hash.
    refresh_token_saved = await save_refresh_token(
        login_result.user_id,
        login_result.session_id,
        refresh_token_value,
    )

    if not refresh_token_saved:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    print(login_result.phone_required)

    return {
        "name": login_result.name,
        "email": login_result.email,
        "accesstoken": access_token,
        "refreshtoken": refresh_token_value,
        'phone_required': login_result.phone_required,
        'profile_required': login_result.profile_required,
        'pwd_change_required': login_result.pwd_change_required,
        'role': login_result.role
    }

# change password


@router.patch('/change/password')
async def verifyPhone(pwd: PasswordReplaceRequest, payload: dict = Depends(verify_user_access_token)):
    await replace_password(user_id=payload['sub'], pwd=pwd.password)

    # Replaces the password from sheet
    await update_password_in_sheet(user_id=payload['sub'], password=pwd.password)

    return {'status': f'Password added Successfully'}


@router.patch('/verify/phone')
async def verifyPhone(phno: PhoneNumberVerify, payload: dict = Depends(verify_user_access_token)):
    await add_phone_number(user_id=payload['sub'], phno=phno.phno)

    return {'status': f'{phno.phno} added Successfully'}

# Profile add   
@router.post("/add/profile", status_code=200, response_model=AddOwnProfileResponse)
async def add_own_profile(
    profile_data: AddOwnProfileRequest,
    payload: dict = Depends(verify_user_access_token)
):
    """Submit profile details for the logged-in user."""
    data_dict = profile_data.model_dump(mode='json')

    await add_user_profile(payload['sub'], data_dict)

    return {
        'status': 'profile created'
    }

#Getting user creds for android
@router.get("/credentials", response_model=UserCredentialsResponse)
async def get_own_credentials(
    payload: dict = Depends(verify_user_access_token)
):
    """Retrieve credentials status for the logged-in user."""
    return await get_user_credentials(payload['sub'])



@router.post("/refresh", response_model=RefreshResponse)
async def refresh(
    payload: dict = Depends(verify_refresh_token),
    token: HTTPAuthorizationCredentials = Depends(security),
) -> dict[str, str]:
    """Rotate a valid refresh token into a new access/refresh token pair."""

    is_valid_refresh_token: bool = await verify_stored_refresh_token(
        payload["session_id"],
        token.credentials,
    )

    if not is_valid_refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    token_user = TokenUser(
        user_id=payload["sub"],
        session_id=payload["session_id"],
    )

    print("A")

    access_token = create_access_token(token_user)
    refresh_token_value = refresh_token(token_user)

    print("A")

    # Each successful refresh replaces the stored token hash.
    refresh_token_saved = await update_new_refresh_token(
        token_user.session_id,
        refresh_token_value,
    )

    if not refresh_token_saved:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not update new refresh token",
        )

    return {
        "accesstoken": access_token,
        "refreshtoken": refresh_token_value,
    }


@router.post("/logout", response_model=LogOutResponse)
async def logout(
    payload: dict = Depends(verify_user_access_token),
) -> dict[str, str]:
    """Invalidate the user's saved refresh token while keeping the API stateless."""

    refresh_token_cleared = await clear_refresh_token(
        payload["session_id"],
    )

    if not refresh_token_cleared:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return {"status": "Logout successful"}
