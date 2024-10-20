from typing import Generator
from redis import Redis
import os
from dotenv import load_dotenv

load_dotenv()

def get_redis_connection() -> Generator[Redis, None, None]:
    redis_client = Redis(
        host=os.getenv("RD_CACHE_SERVER"),
        port=os.getenv("RD_CACHE_PORT"),
        password=os.getenv("RD_CACHE_PASSWORD"),
        decode_responses=True,
    )
    try:
        yield redis_client
    finally:
        redis_client.close()