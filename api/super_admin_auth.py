from fastapi import APIRouter, logger, status
from fastapi import APIRouter, BackgroundTasks, Depends
from Request_and_Response.Requests import SignUpRequest
from Request_and_Response.Responses import (
    SignUpResponse,
)

from celery_worker.tasks import send_email_smtp
from mongodb.db_functions.auth import (UserDetails)
from dependency.token_dependency import verify_super_admin_access_token
from mongodb.db_functions.sadmin_auth import create_user
from security.google_sheet import GoogleSheetError, add_user_to_sheet


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/sadmin/signup",
    response_model=SignUpResponse,
    status_code=status.HTTP_201_CREATED,
)
async def signup(
    signup_cred: SignUpRequest,
    email_send_task: BackgroundTasks,
    payload: dict = Depends(verify_super_admin_access_token)
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
