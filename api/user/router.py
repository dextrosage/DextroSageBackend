from fastapi import APIRouter, Depends, Path
from Request_and_Response.Responses import DeleteAllSessionUserResponse, DeleteUserResponse, DeleteUserSessionResponse, UserDetailsResponse, UserSessionsResponse, AddOwnProfileResponse, GetOwnProfileResponse
from Request_and_Response.Requests import AddOwnProfileRequest
from dependency.token_dependency import verify_user_access_token
from mongodb.db_functions.admin import delete_all_session_by_user_id, delete_member_by_id, get_sessions_of_user_by_id
from mongodb.db_functions.user import delete_own_one_session_by_session_id, get_all_users, add_user_profile, get_user_profile
from security.google_sheet import delete_user_from_sheet

router = APIRouter(
    prefix="/user",
    tags=["UserView"]
)


@router.get("/members", response_model=list[UserDetailsResponse])
async def show_all_users(payload: dict = Depends(verify_user_access_token)):

    return await get_all_users()


@router.get("/sessions", response_model=list[UserSessionsResponse])
async def get_own_sessions_of_user(payload: dict = Depends(verify_user_access_token)):

    return await get_sessions_of_user_by_id(payload['sub'])


@router.delete("/delete/session/{session_id}/user", status_code=200, response_model=DeleteUserSessionResponse)
async def delete_own_one_session_of_user(session_id: str = Path(description="Session Id"),
                                         payload: dict = Depends(verify_user_access_token)):
    '''Deleting a session of member from db'''

    await delete_own_one_session_by_session_id(payload['sub'], session_id)

    return {
        'status': 'Session deleted'
    }


@router.delete("/delete/all/sessions/user", status_code=200, response_model=DeleteAllSessionUserResponse)
async def delete_own_all_sessions_of_user(payload: dict = Depends(verify_user_access_token)):
    '''Deleting member and clearing session of them from db'''

    await delete_all_session_by_user_id(payload['sub'])

    return {
        'status': 'All sessions deleted'
    }


@router.delete("/delete/user/", status_code=200, response_model=DeleteUserResponse)
async def delete_own_user(payload: dict = Depends(verify_user_access_token)):
    '''Deleting member and clearing session of them from db'''

    await delete_member_by_id(payload['sub'])

    # Deleting row from google sheet
    await delete_user_from_sheet(payload['sub'])

    return {
        'status': 'User deleted'
    }

# Own Profile get


@router.get("/profile", status_code=200, response_model=GetOwnProfileResponse)
async def get_own_profile(payload: dict = Depends(verify_user_access_token)):
    """Retrieve profile details for the authenticated user."""
    return await get_user_profile(payload['sub'])

# Others Profile get


@router.get("/member/{user_id}/profile", status_code=200, response_model=GetOwnProfileResponse)
async def get_member_profile(user_id: str = Path(), payload: dict = Depends(verify_user_access_token)):
    """Retrieve profile details for the authenticated user."""
    return await get_user_profile(user_id)
