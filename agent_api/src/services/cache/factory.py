from loguru import logger

import redis
from src.config import Settings
from src.services.cache.client import CacheClient

def make_redis_client(settings:Settings)-> redis.Redis:
    """Create Redis client with connection pooling"""
    redis_settings = settings.redis

    try:
        client = redis.Redis(
            host = redis_settings.host,
            port = redis_settings.port,
            password = redis_settings.password if redis_settings.password else None,
            db = redis_settings.db,
            decode_response = redis_settings.decode_responses,
            socket_timweout = redis_settings.socker_timeout,
            socker_connect_timeout = redis_settings.socket_connect_timeout,
            retry_on_timeout = True,
            retry_on_error  = [redis.ConnectionError, redis.TimeoutError],
        )

        client.ping()
        logger.info(f"Connected to redis at {redis_settings.host}: {redis_settings.port}")
        return client
    
    except redis.ConnectionError as e:
        logger.error(f"Failed to connect to redis: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error catching redis client: {e}")
        raise

def make_cache_client(settings: Settings)-> CacheClient:
    """Create exact match cache client"""
    try:
        redis_client = make_redis_client(settings)
        cache_client = CacheClient(redis_client,settings.redis)
        logger.info("Exact match cache client created successfully")
    except Exception as e:
        logger.error(f"Falied to create cache client: {e}")
        raise