

from fastapi import HTTPException
from pymongo.errors import DuplicateKeyError, PyMongoError

from Request_and_Response.Requests import SignUpRequest
from mongodb.db_functions.auth import UserDetails, generate_password, generate_unique_username
from mongodb.models import User
from security.hash_and_verify import hash_keyword
from mongodb.collections import users


async def create_user(signup_cred: SignUpRequest) -> bool:
    """Create a user when the username is available and return generated email and pwd."""

    # Checking whom can be added by SADMIN
    add_permissions = ["ADMIN", "USER", "SADMIN"]

    if (signup_cred.role not in add_permissions):
        raise HTTPException(status_code=403, detail="Cannot add the role")

    # Generate unique username and password
    username = generate_unique_username(signup_cred.role)
    password = generate_password()

    user = User(
        name=signup_cred.name,
        email=signup_cred.email,
        username=username,
        password=hash_keyword(password),
        role=signup_cred.role,
        phone_verify=False,
        profile_required=True,
        pwd_change_required=True
    )

    try:
        result = await users.insert_one(user.model_dump())
        return UserDetails(user_id=str(result.inserted_id), username=username, password=password)

    except DuplicateKeyError as e:
        # print(e)
        raise HTTPException(
            status_code=409,
            detail="Username, email, or phone number already exists."
        )

    except PyMongoError as e:
        # print(e)
        raise HTTPException(
            status_code=500,
            detail="Database error."
        )
