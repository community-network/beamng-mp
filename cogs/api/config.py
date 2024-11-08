import os

REDIS_HOST = os.getenv("redishost", "")
REDIS_PORT = int(os.getenv("redisport", 6379))
REDIS_PASS = os.getenv("redispass", "")

CACHE_TTL_DEFAULT = os.getenv("CACHE_TTL_DEFAULT", 600)
CACHE_TTL_SERVERS = os.getenv("CACHE_TTL_SERVERS", 10)

CACHE_MAX_AGE_DEFAULT = os.getenv("CACHE_MAX_AGE_DEFAULT", 600)
CACHE_MAX_AGE_SERVERS = os.getenv("CACHE_MAX_AGE_SERVERS", 10)
