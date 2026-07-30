from bson import ObjectId
from fastapi import HTTPException
from pymongo.errors import PyMongoError

from Request_and_Response.Responses import AdminViewResponse
from mongodb.collections import users, sessions, profiles


async def get_all_members(skip: int = 0, limit: int = 10):
    try:
        user_result = await users.find().skip(skip).limit(limit).to_list(length=None)
        
    except PyMongoError:
        raise HTTPException(status_code=500, detail="Database error")

    return [
        AdminViewResponse(
            user_id=str(doc["_id"]),
            name=doc['name'],
            phno= doc['phno'] if 'phno' in doc else "N/A",
            email=doc['email'],
            role=doc['role'],
            connected_users=doc.get('connected_users', []),
            pending_connections=doc.get('pending_connections', []),
            sent_requests=doc.get('sent_requests', [])
        )
        for doc in user_result
    ]


async def get_sessions_of_user_by_id(user_id: str):
    try:
        user_sessions = await sessions.find({'user_id': ObjectId(user_id)}, {
                                      "session_id": 1, '_id': 0}).to_list(None)
        
    except PyMongoError:
        raise HTTPException(status_code=500, detail="Database error")
    
    return user_sessions


async def delete_member_by_id(user_id: str):
    try:
        user_delete_result = await users.delete_one({'_id': ObjectId(user_id)})

        # If user do not exist
        if user_delete_result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="User not found")

        await sessions.delete_many({'user_id': ObjectId(user_id)})
        await profiles.delete_many({'user_id': ObjectId(user_id)})

    except PyMongoError:
        raise HTTPException(status_code=500, detail="Database error")

    # User session being None is fine. And if present gets deleted.


async def delete_one_session_by_session_id(session_id: str):
    
    try:
        result = await sessions.delete_one({'session_id' : session_id})
        
    except PyMongoError:
        raise HTTPException(status_code=500, detail="Database error")

    #If session not found
    if(result.deleted_count == 0):
        raise HTTPException(status_code=404, detail="Session not found")
        
    
async def delete_all_session_by_user_id(user_id: str):
    try:
        result = await sessions.delete_many({'user_id' : ObjectId(user_id)})
        
    except PyMongoError:
        raise HTTPException(status_code=500, detail="Database error")

    #If session not found
    if(result.deleted_count == 0):
        raise HTTPException(status_code=404, detail="Session not found")