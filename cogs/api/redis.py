"""Redis functions"""
import os
import sys
from datetime import timedelta
from typing import Any

import redis.asyncio.client
import redis.asyncio
import redis.asyncio.cluster
import redis

REDIS_HOST = os.getenv("redishost", "")
REDIS_PORT = int(os.getenv("redisport", 6379))
REDIS_PASS = os.getenv("redispass", "")

CACHE_TTL_DEFAULT = os.getenv("CACHE_TTL_DEFAULT", 600)
CACHE_TTL_SERVERS = os.getenv("CACHE_TTL_SERVERS", 10)

CACHE_MAX_AGE_DEFAULT = os.getenv("CACHE_MAX_AGE_DEFAULT", 600)
CACHE_MAX_AGE_SERVERS = os.getenv("CACHE_MAX_AGE_SERVERS", 10)


async def redis_connect() -> redis.asyncio.client.Redis:
    """Connect to db"""
    try:
        global client
        client = redis.asyncio.cluster.RedisCluster(
            host=str(REDIS_HOST),
            port=int(REDIS_PORT),
            password=str(REDIS_PASS),
            socket_timeout=5,
        )
        ping = await client.ping()
        if ping is True:
            return
    except redis.AuthenticationError:
        print("AuthenticationError")
        sys.exit(1)
    except redis.exceptions.RedisClusterException:
        client = redis.asyncio.Redis(
            host=str(REDIS_HOST),
            port=int(REDIS_PORT),
            password=str(REDIS_PASS),
            db=0,
            socket_timeout=5,
        )
        ping = await client.ping()
        if ping is True:
            return


async def get_from_cache(key: str) -> Any:
    """Data from redis."""

    val = await client.get(key)
    return val


async def set_to_cache(key: str, value: str, ttl: int = CACHE_TTL_DEFAULT) -> bool:
    """Data to redis."""

    state = await client.setex(key, timedelta(seconds=ttl), value=value)
    return state
