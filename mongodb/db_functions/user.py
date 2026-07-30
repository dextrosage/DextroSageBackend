from bson import ObjectId
from fastapi import HTTPException
from pymongo.errors import PyMongoError
from Request_and_Response.Responses import AdminViewResponse
from mongodb.collections import sessions, users, profiles, notifications
from datetime import datetime, UTC

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
            role=doc['role'],
            connected_users=doc.get('connected_users', []),
            pending_connections=doc.get('pending_connections', []),
            sent_requests=doc.get('sent_requests', [])
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


async def connect_user(user_id: str, target_user_id: str):
    try:
        user1 = await users.find_one({"_id": ObjectId(user_id)})
        user2 = await users.find_one({"_id": ObjectId(target_user_id)})
        if not user1 or not user2:
            raise HTTPException(status_code=404, detail="User not found")
            
        # Add to pending_connections of target, and sent_requests of user
        await users.update_one(
            {"_id": ObjectId(target_user_id)},
            {"$addToSet": {"pending_connections": user_id}}
        )
        await users.update_one(
            {"_id": ObjectId(user_id)},
            {"$addToSet": {"sent_requests": target_user_id}}
        )

        # Create notification for target user
        await create_notification(target_user_id, f"{user1.get('name', 'Someone')} sent you a connection request.")
    except PyMongoError:
        raise HTTPException(status_code=500, detail="Database error")

async def accept_connection(user_id: str, target_user_id: str):
    try:
        # target_user_id is the one who sent the request (in user_id's pending)
        user1 = await users.find_one({"_id": ObjectId(user_id)})
        user2 = await users.find_one({"_id": ObjectId(target_user_id)})
        if not user1 or not user2:
            raise HTTPException(status_code=404, detail="User not found")
            
        # Add to connected_users for both
        await users.update_one(
            {"_id": ObjectId(user_id)},
            {"$addToSet": {"connected_users": target_user_id}, "$pull": {"pending_connections": target_user_id}}
        )
        await users.update_one(
            {"_id": ObjectId(target_user_id)},
            {"$addToSet": {"connected_users": user_id}, "$pull": {"sent_requests": user_id}}
        )

        await create_notification(target_user_id, f"{user1.get('name', 'Someone')} accepted your connection request.")
    except PyMongoError:
        raise HTTPException(status_code=500, detail="Database error")

async def reject_connection(user_id: str, target_user_id: str):
    try:
        user1 = await users.find_one({"_id": ObjectId(user_id)})
        user2 = await users.find_one({"_id": ObjectId(target_user_id)})
        if not user1 or not user2:
            raise HTTPException(status_code=404, detail="User not found")
            
        # Remove from pending and sent
        await users.update_one(
            {"_id": ObjectId(user_id)},
            {"$pull": {"pending_connections": target_user_id}}
        )
        await users.update_one(
            {"_id": ObjectId(target_user_id)},
            {"$pull": {"sent_requests": user_id}}
        )
    except PyMongoError:
        raise HTTPException(status_code=500, detail="Database error")

async def remove_connection(user_id: str, target_user_id: str):
    try:
        user1 = await users.find_one({"_id": ObjectId(user_id)})
        user2 = await users.find_one({"_id": ObjectId(target_user_id)})
        if not user1 or not user2:
            raise HTTPException(status_code=404, detail="User not found")
            
        # Remove from connected_users
        await users.update_one(
            {"_id": ObjectId(user_id)},
            {"$pull": {"connected_users": target_user_id}}
        )
        await users.update_one(
            {"_id": ObjectId(target_user_id)},
            {"$pull": {"connected_users": user_id}}
        )
    except PyMongoError:
        raise HTTPException(status_code=500, detail="Database error")

async def get_pending_connections(user_id: str):
    try:
        user = await users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        pending_ids = user.get("pending_connections", [])
        pending_object_ids = [ObjectId(uid) for uid in pending_ids if ObjectId.is_valid(uid)]
        
        if not pending_object_ids:
            return []
            
        pending_users = await users.find({"_id": {"$in": pending_object_ids}}).to_list(length=None)
        
        return [
            {
                "user_id": str(doc["_id"]),
                "name": doc.get("name", "Unknown"),
                "email": doc.get("email", ""),
                "role": doc.get("role", "USER")
            } for doc in pending_users
        ]
    except PyMongoError:
        raise HTTPException(status_code=500, detail="Database error")

async def create_notification(user_id: str, content: str):
    try:
        doc = {
            "user_id": user_id,
            "content": content,
            "is_read": False,
            "created_at": datetime.now(UTC)
        }
        await notifications.insert_one(doc)
    except PyMongoError:
        pass # Ignore errors in notification creation

async def get_notifications(user_id: str):
    try:
        cursor = notifications.find({"user_id": user_id, "is_read": False}).sort("created_at", -1)
        docs = await cursor.to_list(length=None)
        return [
            {
                "id": str(doc["_id"]),
                "user_id": doc["user_id"],
                "content": doc["content"],
                "is_read": doc["is_read"],
                "created_at": doc["created_at"].isoformat() if isinstance(doc["created_at"], datetime) else str(doc["created_at"])
            } for doc in docs
        ]
    except PyMongoError:
        raise HTTPException(status_code=500, detail="Database error")

async def mark_notifications_read(user_id: str):
    try:
        await notifications.update_many({"user_id": user_id, "is_read": False}, {"$set": {"is_read": True}})
    except PyMongoError:
        raise HTTPException(status_code=500, detail="Database error")

async def get_user_connections(user_id: str):
    try:
        user = await users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        connected_ids = user.get("connected_users", [])
        connected_object_ids = [ObjectId(uid) for uid in connected_ids if ObjectId.is_valid(uid)]
        
        if not connected_object_ids:
            return []
            
        connected_users = await users.find({"_id": {"$in": connected_object_ids}}).to_list(length=None)
        
        return [
            {
                "user_id": str(doc["_id"]),
                "name": doc.get("name", "Unknown"),
                "email": doc.get("email", ""),
                "role": doc.get("role", "USER")
            } for doc in connected_users
        ]
    except PyMongoError:
        raise HTTPException(status_code=500, detail="Database error")