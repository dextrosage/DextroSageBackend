from pydantic import BaseModel, EmailStr


class SignUpResponse(BaseModel):
    """Response body expected by the signup endpoint."""

    status: str
    email: EmailStr


class LoginResponse(BaseModel):
    """Response body expected by the login endpoint."""

    name: str
    email: EmailStr
    accesstoken: str
    refreshtoken: str
    phone_required: bool
    profile_required: bool
    pwd_change_required: bool
    role: str

class RefreshResponse(BaseModel):
    """Response body expected by the refresh endpoint."""
    
    accesstoken: str
    refreshtoken: str
    
class LogOutResponse(BaseModel):
    """Response body expected by the logout endpoint."""

    status: str
    
class AdminViewResponse(BaseModel):
    user_id: str
    name: str
    phno: str
    email: str
    role: str

class UserDetailsResponse(BaseModel):
    user_id: str
    name: str
    phno: str
    email: str
    role: str

class UserSessionsResponse(BaseModel):
    session_id: str

class DeleteUserResponse(BaseModel):
    status: str
    
class DeleteUserSessionResponse(BaseModel):
    status: str
    
class DeleteAllSessionUserResponse(BaseModel):
    '''Request body for deleting all sessions of member from the db'''
    
    status: str
    
class PhnoNumberResponse(BaseModel):
    status: str


class AddOwnProfileResponse(BaseModel):
    status: str


class GetOwnProfileResponse(BaseModel):
    linkedin: str
    github: str
    skills: list[str]
    experience: list[dict]
    education: list[dict]
    address: dict

class AnnouncementResponse(BaseModel):
    id: str
    title: str
    content: str
    author_id: str
    author_name: str
    author_role: str
    created_at: str
    updated_at: str
    video_links: list[str] = []

class StatusResponse(BaseModel):
    status: str


class UserCredentialsResponse(BaseModel):
    name: str
    email: EmailStr
    role: str
    phone_required: bool
    profile_required: bool
    pwd_change_required: bool
    phno: str | None = None