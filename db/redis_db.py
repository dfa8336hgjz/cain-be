from fastapi import Depends, HTTPException
from typing import Generator
from redis import Redis
import os
from dotenv import load_dotenv

load_dotenv()

def get_redis_connection() -> Generator[Redis, None, None]:
    redis_client = Redis(
        host=os.getenv("REDIS_SERVER"),
        port=os.getenv("REDIS_PORT"),
        password=os.getenv("REDIS_PASSWORD"),
        decode_responses=True,
    )
    try:
        yield redis_client
    finally:
        redis_client.close()
    
class RedisService:
    def __init__(self, redis_client: Redis = Depends(get_redis_connection)):
        self.redis_client = redis_client

    async def add_token_to_blacklist(self, token: str):
        try:
            self.redis_client.setex(f"blacklist:{token}", 7 * 24 * 60 * 60, "")
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail="Cannot add token to blacklist.",
            )

    async def is_token_blacklisted(self, token: str):
        try:
            return self.redis_client.get(f"blacklist:{token}") is not None
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail="Internal server error.",
            )