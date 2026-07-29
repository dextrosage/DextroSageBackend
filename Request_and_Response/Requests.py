from datetime import date
from pydantic import BaseModel, EmailStr, Field, HttpUrl


class SignUpRequest(BaseModel):
    """Request body expected by the signup endpoint."""
    name: str
    email: EmailStr
    role: str = "USER"


class LoginRequest(BaseModel):
    """Request body expected by the login endpoint."""

    username: str
    password: str

class PasswordReplaceRequest(BaseModel):
    password: str

    
class PhoneNumberVerify(BaseModel):
    phno: str = Field(max_length=10,min_length=10)


class Experience(BaseModel):
    company: str
    designation: str
    start_date: date
    end_date: date | None
    currently_working: bool


class Education(BaseModel):
    college: str
    degree: str
    branch: str
    start_date: date
    end_date: date


class Address(BaseModel):
    street: str
    city: str
    state: str
    country: str
    pincode: str


class AddOwnProfileRequest(BaseModel):
    linkedin: HttpUrl
    github: HttpUrl
    skills: list[str]
    experience: list[Experience]
    education: list[Education]
    address: Address


class AnnouncementCreateRequest(BaseModel):
    title: str = Field(..., max_length=200)
    content: str = Field(..., max_length=50000)
    video_links: list[str] = Field(default=[])

class AnnouncementUpdateRequest(BaseModel):
    title: str | None = Field(None, max_length=200)
    content: str | None = Field(None, max_length=50000)
    video_links: list[str] | None = Field(None)