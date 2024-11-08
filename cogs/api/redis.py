"""Redis functions"""

import sys
import logging
from datetime import timedelta
from typing import Any

import redis.asyncio.client
import redis.asyncio
import redis.asyncio.cluster
import redis

from . import Singleton
from . import config


class RedisClient(metaclass=Singleton):
    client: redis.asyncio.Redis

    def __init__(self):
        self.logger = logging.getLogger("redis")

    async def redis_connect(self):
        """Connect to the redis host"""
        try:
            self.client = redis.asyncio.Redis(
                host=str(config.REDIS_HOST),
                port=int(config.REDIS_PORT),
                password=str(config.REDIS_PASS),
                socket_timeout=5,
            )
            ping = await self.client.ping()
            if ping is True:
                return
        except redis.AuthenticationError:
            self.logger.error("Redis authentication error!")
            sys.exit(1)
        except redis.exceptions.ConnectionError:
            self.logger.error("Redis ping error, will retry on use.")
            return
        except redis.exceptions.TimeoutError:
            self.logger.error("Redis timeout error, will retry on use.")
            return

    async def get_from_cache(self, key: str) -> Any:
        """Data from redis."""
        val = None
        try:
            val = await self.client.get(key)
        except Exception as e:
            self.logger.error("failed to get cache! %s", e)
        return val

    async def set_to_cache(
        self, key: str, value: str, ttl: int = config.CACHE_TTL_DEFAULT
    ) -> bool:
        """Data to redis."""
        if ttl is None:
            return True
        try:
            state = await self.client.setex(key, timedelta(seconds=ttl), value=value)
            return state
        except Exception as e:
            self.logger.error("failed to set cache! %s", e)
            return False
