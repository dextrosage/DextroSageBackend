from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from auth_jwt.create_tokens import verify_token
from mongodb.db_functions.auth import get_user_role, is_refresh_token_in_db

security = HTTPBearer()


# Standard 401 response raised whenever bearer-token validation fails.
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid token",
    headers={"WWW-Authenticate": "Bearer"},
)

###Main functions
#Verifying user tokens
async def verify_user_access_token(
    token: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Require a valid access token for routes that read protected resources."""

    return await _verify_user_token_type(token, "access")

#Verifying admin tokens
async def verify_admin_access_token(
    token: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """Require a valid access token for routes that read protected resources."""

    return await _verify_admin_token_type(token, "access")

#Verifying super-admin tokens
async def verify_super_admin_access_token(
    token: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """Require a valid access token for routes that read protected resources."""

    return await _verify_super_admin_token_type(token, "access")



async def verify_refresh_token(
    token: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Require a valid refresh token for token rotation routes."""

    return await _verify_user_token_type(token, "refresh")


###Helper fucntions
async def _verify_user_token_type(
    token: HTTPAuthorizationCredentials,
    expected_type: str
    ) -> dict:
    """Decode a bearer token and enforce that it has the expected token type."""

    payload = verify_token(token.credentials)

    if payload is None or payload.get("type") != expected_type:
        raise credentials_exception
    
    rt_in_db = await is_refresh_token_in_db(payload["session_id"])

    if not rt_in_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User already logged out",
        )

    return payload

async def _verify_admin_token_type(
    token: HTTPAuthorizationCredentials,
    expected_type: str
    ) -> dict:
    """Decode a bearer token and enforce that it has the expected token type."""

    payload = verify_token(token.credentials)

    if payload is None or payload.get("type") != expected_type:
        raise credentials_exception

    #Checking if the token belongs to an admin or not
    user_role = await get_user_role(payload.get("sub"))
    
    if(user_role == "USER"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin priviledges needed",
        )
    
    #Checking if the user is already logged out or not
    rt_in_db = await is_refresh_token_in_db(payload["session_id"])

    if not rt_in_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User already logged out",
        )

    
    return payload

async def _verify_super_admin_token_type(
    token: HTTPAuthorizationCredentials,
    expected_type: str
    ) -> dict:
    """Decode a bearer token and enforce that it has the expected token type."""

    payload = verify_token(token.credentials)

    if payload is None or payload.get("type") != expected_type:
        raise credentials_exception

    #Checking if the token belongs to an admin or not
    user_role = await get_user_role(payload.get("sub"))
    
    if(user_role != "SADMIN"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super Admin priviledges needed",
        )
    
    #Checking if the user is already logged out or not
    rt_in_db = await is_refresh_token_in_db(payload["session_id"])

    if not rt_in_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User already logged out",
        )

    
    return payload

