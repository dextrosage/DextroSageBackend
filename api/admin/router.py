from fastapi import APIRouter, Depends, Path, Query
from Request_and_Response.Requests import AddOwnProfileRequest
from Request_and_Response.Responses import AddOwnProfileResponse, DeleteAllSessionUserResponse, DeleteUserResponse, DeleteUserSessionResponse, GetOwnProfileResponse, UserDetailsResponse, UserSessionsResponse
from dependency.token_dependency import verify_admin_access_token
from mongodb.db_functions.admin import delete_all_session_by_user_id, delete_member_by_id, delete_one_session_by_session_id, get_all_members, get_sessions_of_user_by_id
from mongodb.db_functions.auth import get_user_role
from mongodb.db_functions.user import add_user_profile, delete_own_one_session_by_session_id, get_user_profile
from security.google_sheet import delete_user_from_sheet

router = APIRouter(
    prefix="/admin",
    tags=["AdminView"]
)


@router.get("/members", response_model=list[UserDetailsResponse])
async def show_all_members(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50),
    payload: dict = Depends(verify_admin_access_token)
):
    
    return await get_all_members(skip=skip, limit=limit)


@router.get("/member/sessions", response_model=list[UserSessionsResponse])
async def get_sessions_of_member(payload: dict = Depends(verify_admin_access_token)):

    return await get_sessions_of_user_by_id(payload['sub'])


@router.delete("/delete/session/{session_id}/member", status_code=200, response_model=DeleteUserSessionResponse)
async def delete_one_session_of_member(session_id: str = Path(description="Session Id"),
                                     payload: dict = Depends(verify_admin_access_token)):
    '''Deleting a session of member from db'''

    await delete_own_one_session_by_session_id(payload['sub'],session_id)

    return {
        'status': 'Session deleted'
    }


@router.delete("/delete/all/sessions/member/", status_code=200, response_model=DeleteAllSessionUserResponse)
async def delete_all_sessions_of_member(payload: dict = Depends(verify_admin_access_token)):
    '''Deleting member and clearing session of them from db'''

    # user_role = get_user_role(payload['sub'])

    # if user_role == "USER" and payload['sub'] != user_id:
    #     raise HTTPException(status_code=403, detail="Access not granted")

    await delete_all_session_by_user_id(payload['sub'])

    return {
        'status': 'All sessions deleted'
    }


@router.delete("/delete/members", status_code=200, response_model=DeleteUserResponse)
async def delete_members(payload: dict = Depends(verify_admin_access_token)):
    '''Deleting member and clearing session of them from db'''

    await delete_member_by_id(payload['sub'])

    #Deleting row from google sheet
    await delete_user_from_sheet(payload['sub'])
    
    return {
        'status': 'User deleted'
    }


#Profile get
@router.get("/member/{user_id}/profile", status_code=200, response_model=GetOwnProfileResponse)
async def get_member_profile(user_id: str = Path(), payload: dict = Depends(verify_admin_access_token)):
    """Retrieve profile details for the authenticated user."""
    return await get_user_profile(user_id)

#Own Profile get
@router.get("/member/profile", status_code=200, response_model=GetOwnProfileResponse)
async def get_own_member_profile(payload: dict = Depends(verify_admin_access_token)):
    """Retrieve profile details for the authenticated user."""
    return await get_user_profile(payload['sub'])
