from dataclasses import dataclass
import secrets
import string
import uuid

from bson import ObjectId
from fastapi import HTTPException

from Request_and_Response.Requests import SignUpRequest
from mongodb.models import User, UserSession
from security.hash_and_verify import hash_keyword, verify_keyword

from mongodb.collections import sessions, users
from pymongo.errors import DuplicateKeyError, PyMongoError


def generate_unique_username(role: str):
    prefix = role
    unique_part = uuid.uuid4().hex[:8].upper()
    return f"{prefix}-{unique_part}"


def generate_password(length: int = 12) -> str:
    alphabet = (
        string.ascii_letters +
        string.digits +
        "!@#$%^&*"
    )

    return "".join(
        secrets.choice(alphabet)
        for _ in range(length)
    )


@dataclass
class UserDetails:
    user_id: str
    username: str
    password: str


async def create_user(signup_cred: SignUpRequest) -> bool:
    """Create a user when the username is available and return generated email and pwd."""

    # Checking whom can be added by SADMIN
    add_permissions = ["ADMIN", "USER"]

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
        return UserDetails(str(result.inserted_id), username=username, password=password)

    except DuplicateKeyError as e:
        print(e)
        raise HTTPException(
            status_code=409,
            detail="Username, email, or phone number already exists."
        )

    except PyMongoError as e:
        print(e)
        raise HTTPException(
            status_code=500,
            detail="Database error."
        )


@dataclass
class LoginResult:
    success: bool
    user_id: str | None = None
    session_id: str | None = None
    phone_required: bool = False
    profile_required: bool = False
    pwd_change_required: bool = False
    role: str | None = None
    name: str | None = None
    email: str | None = None


async def verify_login_user(
    username: str,
    password: str
) -> LoginResult:
    """Validate login credentials against the stored password hash and fetch the role."""

    try:
        user = await users.find_one(
            {"username": username},
            {
                "_id": 1,
                'password': 1,
                'role': 1,
                "phone_verify": 1,
                "profile_required": 1,
                "pwd_change_required": 1,
                "name": 1,
                'email': 1
            }
        )

    except PyMongoError:
        return LoginResult(False)

    # If user exists
    if user is None:
        return LoginResult(False)

    # Verify password
    if not verify_keyword(password, user['password']):
        return LoginResult(False)

    actual_role = user['role']

    # Generating the session id
    session_id = str(uuid.uuid4())

    phone_req = not (user['phone_verify'])
    profile_req = user.get('profile_required', True)
    pwd_change_required = user['pwd_change_required']
    name = user['name']
    email = user['email']

    return LoginResult(True, str(user['_id']), session_id=session_id, phone_required=phone_req, profile_required=profile_req, pwd_change_required=pwd_change_required, role=actual_role, name=name, email=email)


async def save_refresh_token(
    user_id: str,
    session_id: str,
    refresh_token_value: str,
) -> bool:
    """Store a hashed refresh token in sessions table for later rotation and logout checks."""

    try:
        user_session = UserSession(
            session_id=session_id,
            user_id=ObjectId(user_id),
            refreshtoken=hash_keyword(refresh_token_value),
        )

        await sessions.insert_one(user_session.model_dump())
        return True

    except DuplicateKeyError as e:
        raise HTTPException(
            status_code=409,
            detail="Session already exists."
        )

    except PyMongoError as e:
        return False


async def verify_stored_refresh_token(
    session_id: str,
    refresh_token_value: str,
) -> bool:
    """Confirm that a presented refresh token matches the stored hash."""

    try:
        result = await sessions.find_one(
            {'session_id': session_id},
            {'refreshtoken': 1}
        )

    except PyMongoError as e:
        print(e)
        return False

    if result is None:
        raise HTTPException(status_code=409, detail="Already logged out")

    print(verify_keyword(refresh_token_value, result['refreshtoken']))

    return verify_keyword(refresh_token_value, result['refreshtoken'])


async def update_new_refresh_token(
    session_id: str,
    refreshtoken: str,
) -> bool:
    """Replace the stored refresh-token hash after a successful refresh."""

    try:
        result = await sessions.update_one(
            {"session_id": session_id},
            {"$set": {'refreshtoken': hash_keyword(refreshtoken)}}
        )
        return result.matched_count > 0

    except PyMongoError as e:
        print(e)
        return False


async def clear_refresh_token(
    session_id: str,
) -> bool:
    """Remove the stored refresh token hash when a user logs out."""

    try:
        result = await sessions.delete_one({"session_id": session_id})

        if result.deleted_count > 0:
            return True

        return False
    except PyMongoError:
        return False

# Change password


async def replace_password(user_id: str, pwd: str):
    try:
        # If pwd already changed
        user = await users.find_one(
            {"_id": ObjectId(user_id)},
            {"pwd_change_required": 1}
        )

        if not user['pwd_change_required']:
            raise HTTPException(
                status_code=409,
                detail="Pwd already changed."
            )

        # If not then replace pwd and make it True
        result = await users.update_one({'_id': ObjectId(user_id)}, {"$set": {'password': hash_keyword(pwd), 'pwd_change_required': False}})

    except DuplicateKeyError:
        raise HTTPException(status_code=403, detail="Password already exists")

    except PyMongoError:
        raise HTTPException(status_code=500, detail="Database Error")

    if result.matched_count == 0:
        raise HTTPException(404, "User not found")


# Adding phno in db
async def add_phone_number(user_id: str, phno: str):
    try:
        # If phno already verified
        user = await users.find_one(
            {"_id": ObjectId(user_id)},
            {"phone_verify": 1}
        )

        if user['phone_verify']:
            raise HTTPException(
                status_code=409,
                detail="Phone already verified."
            )

        # If not then add phno and make it True
        result = await users.update_one({'_id': ObjectId(user_id)}, {"$set": {'phno': phno, 'phone_verify': True}})

    except DuplicateKeyError:
        raise HTTPException(
            status_code=403, detail="Phone number already exists")

    except PyMongoError:
        raise HTTPException(status_code=500, detail="Database Error")

    if result.matched_count == 0:
        raise HTTPException(404, "User not found")


# Used in token_depenency.py


async def get_user_role(
    user_id: str,
) -> str:
    """getting the role of the user_id"""

    result = await users.find_one({'_id': ObjectId(user_id)}, {'role': 1})

    if result is None:
        raise HTTPException(status_code=401, detail="User do not exist")

    return result['role']


async def is_refresh_token_in_db(
    session_id: str,
) -> bool:
    """Return whether a login session has a stored refresh token."""

    try:
        result = await sessions.find_one({"session_id": session_id})
    except PyMongoError:
        return False

    return result is not None


@dataclass
class UserCredentials:
    name: str
    email: str
    role: str
    phone_required: bool
    profile_required: bool
    pwd_change_required: bool
    phno: str | None = None


async def get_user_credentials(user_id: str) -> UserCredentials:
    try:
        user = await users.find_one(
            {"_id": ObjectId(user_id)},
            {
                "name": 1,
                "email": 1,
                "phno": 1,
                "phone_verify": 1,
                "profile_required": 1,
                "pwd_change_required": 1,
                'role' : 1
            }
        )
    except PyMongoError:
        raise HTTPException(status_code=500, detail="Database Error")

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return UserCredentials(
        name=user['name'],
        email=user['email'],
        role=user['role'],
        phno=user.get('phno'),
        phone_required=not user['phone_verify'],
        profile_required=user['profile_required'],
        pwd_change_required=user['pwd_change_required']
    )
