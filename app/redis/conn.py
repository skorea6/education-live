from typing import Optional
from aioredis import Redis, from_url


class RedisCache:

    def __init__(self):
        self.redis_cache: Optional[Redis] = None

    async def init_cache(self):
        self.redis_cache = await from_url("redis://127.0.0.1:6379", decode_responses=True)  # Connecting to database

    async def keys(self, pattern):
        return await self.redis_cache.keys(pattern)

    async def set(self, key, value):
        return await self.redis_cache.set(key, value)

    async def get(self, key):
        return await self.redis_cache.get(key)

    async def expire(self, key, timeout):
        return await self.redis_cache.expire(key, timeout)

    async def hset(self, name, key, value):
        return await self.redis_cache.hset(name, key, value)

    async def hget(self, name, key):
        return await self.redis_cache.hget(name, key)

    async def hdel(self, name, key):
        return await self.redis_cache.hdel(name, key)

    async def delete(self, name):
        return await self.redis_cache.delete(name)

    async def close(self):
        await self.redis_cache.close()
        await self.redis_cache.wait_closed()


redis_cache = RedisCache()
