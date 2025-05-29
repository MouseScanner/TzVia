import redis
import json
import hashlib
import os
from typing import Optional, List, Dict

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

class CacheManager:
    def __init__(self, ttl: int = 3600):
        self.ttl = ttl
        self.prefix = "similarity_cache:"
    
    def _generate_key(self, text: str) -> str:
        text_hash = hashlib.md5(text.encode()).hexdigest()
        return f"{self.prefix}{text_hash}"
    
    def get_cached_result(self, text: str) -> Optional[List[Dict]]:
        key = self._generate_key(text)
        try:
            cached_data = redis_client.get(key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            print(f"Ошибка при получении из кэша: {e}")
        return None
    
    def cache_result(self, text: str, result: List[Dict]) -> None:
        key = self._generate_key(text)
        try:
            redis_client.setex(key, self.ttl, json.dumps(result))
        except Exception as e:
            print(f"Ошибка при сохранении в кэш: {e}")
    
    def clear_cache(self) -> None:
        try:
            keys = redis_client.keys(f"{self.prefix}*")
            if keys:
                redis_client.delete(*keys)
        except Exception as e:
            print(f"Ошибка при очистке кэша: {e}")

cache_manager = CacheManager() 