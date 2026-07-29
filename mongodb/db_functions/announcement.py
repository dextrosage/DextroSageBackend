from datetime import datetime
from bson import ObjectId
from fastapi import HTTPException
from mongodb.collections import announcements, users

async def create_announcement(title: str, content: str, author_id: str):
    author = await users.find_one({"_id": ObjectId(author_id)})
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
        
    announcement_data = {
        "title": title,
        "content": content,
        "author_id": author_id,
        "author_name": author.get("name", "Admin"),
        "author_role": author.get("role", "ADMIN"),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = await announcements.insert_one(announcement_data)
    return str(result.inserted_id)

async def get_all_announcements(skip: int = 0, limit: int = 10):
    cursor = announcements.find().sort("created_at", -1).skip(skip).limit(limit)
    results = []
    async for document in cursor:
        results.append({
            "id": str(document["_id"]),
            "title": document["title"],
            "content": document["content"],
            "author_id": document["author_id"],
            "author_name": document["author_name"],
            "author_role": document.get("author_role", "ADMIN"),
            "created_at": document["created_at"].isoformat() + "Z",
            "updated_at": document["updated_at"].isoformat() + "Z"
        })
    return results

async def update_announcement(announcement_id: str, title: str | None, content: str | None):
    update_data = {"updated_at": datetime.utcnow()}
    if title is not None:
        update_data["title"] = title
    if content is not None:
        update_data["content"] = content
        
    result = await announcements.update_one(
        {"_id": ObjectId(announcement_id)},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Announcement not found")
        
async def delete_announcement(announcement_id: str):
    result = await announcements.delete_one({"_id": ObjectId(announcement_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Announcement not found")
