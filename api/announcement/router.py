from fastapi import APIRouter, Depends, Path, Query
from Request_and_Response.Requests import AnnouncementCreateRequest, AnnouncementUpdateRequest
from Request_and_Response.Responses import AnnouncementResponse, StatusResponse
from dependency.token_dependency import verify_admin_access_token, verify_user_access_token
from mongodb.db_functions.announcement import (
    create_announcement,
    get_all_announcements,
    update_announcement,
    delete_announcement
)

router = APIRouter(
    prefix="/announcements",
    tags=["Announcements"]
)

@router.get("", response_model=list[AnnouncementResponse])
async def get_announcements(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50),
    payload: dict = Depends(verify_user_access_token)
):
    """Retrieve all announcements. Available to all authenticated users."""
    return await get_all_announcements(skip=skip, limit=limit)

@router.post("/admin", status_code=201, response_model=StatusResponse)
async def create_new_announcement(
    request: AnnouncementCreateRequest,
    payload: dict = Depends(verify_admin_access_token)
):
    """Create a new announcement. Only for ADMIN and SADMIN."""
    await create_announcement(
        title=request.title,
        content=request.content,
        author_id=payload['sub']
    )
    return {"status": "Announcement created"}

@router.put("/admin/{announcement_id}", response_model=StatusResponse)
async def update_existing_announcement(
    request: AnnouncementUpdateRequest,
    announcement_id: str = Path(...),
    payload: dict = Depends(verify_admin_access_token)
):
    """Update an existing announcement. Only for ADMIN and SADMIN."""
    await update_announcement(
        announcement_id=announcement_id,
        title=request.title,
        content=request.content
    )
    return {"status": "Announcement updated"}

@router.delete("/admin/{announcement_id}", response_model=StatusResponse)
async def delete_existing_announcement(
    announcement_id: str = Path(...),
    payload: dict = Depends(verify_admin_access_token)
):
    """Delete an existing announcement. Only for ADMIN and SADMIN."""
    await delete_announcement(announcement_id)
    return {"status": "Announcement deleted"}
