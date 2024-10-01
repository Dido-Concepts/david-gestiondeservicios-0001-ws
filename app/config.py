from os import getenv

from aiocache import caches

REDIS_ENDPOINT = getenv("REDIS_ENDPOINT", "")
REDIS_PORT = getenv("REDIS_PORT", "")
REDIS_PASSWORD = getenv("REDIS_PASSWORD", "")


def configure_cache() -> None:
    caches.set_config(
        {
            "default": {
                "cache": "aiocache.RedisCache",
                "endpoint": REDIS_ENDPOINT,
                "port": REDIS_PORT,
                "password": REDIS_PASSWORD,
                "timeout": 5,
                "db": 0,
                "serializer": {"class": "aiocache.serializers.JsonSerializer"},
                "plugins": [
                    {"class": "aiocache.plugins.HitMissRatioPlugin"},
                    {"class": "aiocache.plugins.TimingPlugin"},
                ],
            }
        }
    )
