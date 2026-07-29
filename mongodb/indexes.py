from mongodb.collections import users, sessions, announcements

async def init_indexes():

    #Indexes for users collection
    await users.create_index(
        "email",
        unique=True
    )

    await users.create_index(
        "username",
        unique=True
    )
    
    #Index for sessions collection
    await sessions.create_index(
        "session_id",
        unique=True
    )

    # Index for announcements collection (descending sort optimization)
    await announcements.create_index(
        [("created_at", -1)]
    )
