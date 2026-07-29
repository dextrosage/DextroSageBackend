import os

from dotenv import load_dotenv
from redis.asyncio import Redis

load_dotenv()

redis_link = os.getenv("REDIS_URL")

redis = Redis.from_url(
    os.getenv("REDIS_URL"),
    decode_responses=True,
)