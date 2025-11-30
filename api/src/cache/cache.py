from typing import Any, Optional
from src.logger.logger import logger
import asyncio
import os

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

class Cache:
    def __init__(
        self,
        host: str = os.environ.get("REDIS_HOST", "localhost"),
        port: int = int(os.environ.get("REDIS_PORT", 6379)),
        db: int = int(os.environ.get("REDIS_DB", 0)),
        default_ttl: int = int(os.environ.get("REDIS_DEFAULT_TTL", 600)),
    ):
        """
        Hybrid Cache: Uses Redis if available, else falls back to in-memory dict.
        default_ttl: default cache time in seconds (default 600s = 10 minutes)
        """
        self.default_ttl = default_ttl
        self.redis = None
        self.use_redis = False
        self.local_cache = {}

        if REDIS_AVAILABLE:
            self.redis = redis.Redis(host=host, port=port, db=db, decode_responses=True)

    async def init(self):
        """Check Redis availability at startup."""
        if self.redis:
            try:
                await self.redis.ping()
                self.use_redis = True
            except Exception:
                self.use_redis = False
                self.local_cache = {}
                logger.warning("Redis not available, falling back to in-memory cache.", module="Cache", label="CACHE")
        else:
            self.local_cache = {}

    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        ttl = ttl or self.default_ttl
        if self.use_redis:
            try:
                try:
                    await self.redis.delete(key)
                except Exception as e:
                    logger.warning(f"Redis delete failed (non-critical): {e}", module="Cache", label="CACHE")
                await self.redis.set(key, value, ex=ttl)
                return  # Successfully set in Redis
            except Exception as e:
                logger.warning(f"Redis set failed, falling back to in-memory cache: {e}", module="Cache", label="CACHE")
                self.use_redis = False
                # Fall through to in-memory cache
        # Use in-memory cache (either Redis not available or Redis failed)
        try:
            self.local_cache[key] = {"value": value, "ttl": ttl, "set_time": asyncio.get_event_loop().time()}
        except Exception as e:
            logger.error(f"Failed to set value in in-memory cache: {e}", module="Cache", label="CACHE")
            raise

    async def get(self, key: str) -> Any:
        if self.use_redis:
            try:
                return await self.redis.get(key)
            except Exception:
                logger.error("Redis get failed, falling back to in-memory cache.", module="Cache", label="CACHE")
                self.use_redis = False
                return await self.get(key)
        else:
            item = self.local_cache.get(key)
            if not item:
                return None
            # Check TTL
            if item["ttl"] is not None:
                elapsed = asyncio.get_event_loop().time() - item["set_time"]
                if elapsed > item["ttl"]:
                    await self.delete(key)
                    return None
            return item["value"]

    async def delete(self, key: str):
        if self.use_redis:
            try:
                await self.redis.delete(key)
            except Exception:
                logger.error("Redis delete failed, using in-memory cache.", module="Cache", label="CACHE")
                self.use_redis = False
                await self.delete(key)
        else:
            self.local_cache.pop(key, None)

    async def clear(self):
        if self.use_redis:
            try:
                await self.redis.flushdb()
            except Exception:
                logger.error("Redis flush failed, using in-memory cache.", module="Cache", label="CACHE")
                self.use_redis = False
                await self.clear()
        else:
            self.local_cache.clear()


# Create cache instance using dynamic environment variables
cache = Cache(default_ttl=600)

