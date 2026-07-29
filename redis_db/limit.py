from fastapi import HTTPException, Request

from redis_db.redis_instance import redis

MAX_ATTEMPTS = 5
WINDOW_SECONDS = 35

def get_login_key(username: str, req: Request):
    return f"login:{username.lower()}:{req.client.host}"

async def check_login_rate_limit(key: str):

    try:
        attempts = await redis.get(key)

        if attempts is None:
            return

        if int(attempts) >= MAX_ATTEMPTS:
            ttl = await redis.ttl(key)

            raise HTTPException(
                status_code=429,
                detail=f"Too many login attempts. Try again in {ttl} seconds."
            )

    except HTTPException:
        raise

    except Exception as e:
        print(f"Redis error: {e}")

async def record_failed_login(key: str):
    
    try:
        attempts = await redis.incr(key)

        if attempts == 1:
            await redis.expire(key, WINDOW_SECONDS)
    
    except Exception as e:
        return
    

async def clear_login_limit(key: str):
    
    try:
        await redis.delete(key)
    
    except Exception as e:
        return