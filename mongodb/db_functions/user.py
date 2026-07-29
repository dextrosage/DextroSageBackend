from bson import ObjectId
from fastapi import HTTPException
from pymongo.errors import PyMongoError
from Request_and_Response.Responses import AdminViewResponse
from mongodb.collections import sessions, users, profiles

async def get_all_users():
    try:
        user_result = await users.find({'role':"USER"}).to_list(length=None)

    except PyMongoError:
        raise HTTPException(status_code=500, detail="Database error")

    return [
        AdminViewResponse(
            user_id=str(doc["_id"]),
            name=doc['name'],
            phno=doc['phno'] if 'phno' in doc else "N/A",
            email=doc['email'],
            role=doc['role']
        )
        for doc in user_result
    ]

async def delete_own_one_session_by_session_id(user_id: str,session_id: str):
    
    try:
        result = await sessions.delete_one({'user_id' : ObjectId(user_id),'session_id' : session_id})
        
    except PyMongoError:
        raise HTTPException(status_code=500, detail="Database error")

    #If session not found
    if(result.deleted_count == 0):
        raise HTTPException(status_code=404, detail="Session not found")


async def add_user_profile(user_id: str, profile_data: dict) -> None:
    """Inserts user profile if profile_required is True, then updates it to False."""
    try:
        user = await users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # If profile_required is False, profile already exists
        if not user.get("profile_required", True):
            raise HTTPException(status_code=409, detail="already profile exists")

        # Create profile document with user_id as the primary key _id
        profile_doc = {
            "_id": ObjectId(user_id),
            **profile_data
        }

        await profiles.insert_one(profile_doc)

        # Update user's profile_required flag to False
        await users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"profile_required": False}}
        )

    except PyMongoError:
        raise HTTPException(status_code=500, detail="Database error")


async def get_user_profile(user_id: str) -> dict:
    """Retrieves profile document by user ID."""
    try:
        profile = await profiles.find_one({"_id": ObjectId(user_id)})
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")

        # Strip database _id primary key before returning
        profile.pop("_id", None)
        return profile

    except PyMongoError:
        raise HTTPException(status_code=500, detail="Database error")