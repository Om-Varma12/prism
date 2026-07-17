"""
Cache service wrapper for Catalyst Cache operations with JSON serialization.
"""

import json
import hashlib
import os
from typing import Optional, Any


class CacheService:
    """Wrapper for Catalyst Cache operations with JSON serialization."""
    
    def __init__(self, segment_service):
        self.segment = segment_service
        self.disabled = os.getenv("DISABLE_CACHE", "false").lower() == "true"
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value and deserialize JSON."""
        if self.disabled:
            return None
        try:
            result = self.segment.get(key)
            if result and 'cache_value' in result:
                return json.loads(result['cache_value'])
            return None
        except Exception as e:
            print(f"[Cache] Get error for key {key}: {e}")
            return None
    
    def put(self, key: str, value: Any, expiry_in_hours: int = 48) -> bool:
        """Cache value with JSON serialization."""
        if self.disabled:
            return False
        try:
            json_value = json.dumps(value)
            self.segment.put(key, json_value, expiry_in_hours)
            print(f"[Cache] Put success for key: {key}")
            return True
        except Exception as e:
            print(f"[Cache] Put error for key {key}: {e}")
            return False
    
    def update(self, key: str, value: Any, expiry_in_hours: int = 48) -> bool:
        """Update cached value with JSON serialization."""
        if self.disabled:
            return False
        try:
            json_value = json.dumps(value)
            self.segment.update(key, json_value, expiry_in_hours)
            print(f"[Cache] Update success for key: {key}")
            return True
        except Exception as e:
            print(f"[Cache] Update error for key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete cached value."""
        if self.disabled:
            return False
        try:
            self.segment.delete(key)
            print(f"[Cache] Delete success for key: {key}")
            return True
        except Exception as e:
            print(f"[Cache] Delete error for key {key}: {e}")
            return False
    
    def get_value(self, key: str) -> Optional[str]:
        """Get raw string value."""
        if self.disabled:
            return None
        try:
            result = self.segment.get_value(key)
            if result and 'cache_value' in result:
                return result['cache_value']
            return None
        except Exception as e:
            print(f"[Cache] Get value error for key {key}: {e}")
            return None


def generate_cache_key(prefix: str, *args) -> str:
    """
    Generate consistent cache key from arguments using MD5 hashing.
    
    Args:
        prefix: Cache key prefix (e.g., "chat:query", "analytics:hotspots")
        *args: Variable arguments to include in the key
        
    Returns:
        Formatted cache key with MD5 hash
    """
    key_string = ":".join(str(arg) for arg in args)
    hash_value = hashlib.md5(key_string.encode()).hexdigest()
    return f"{prefix}:{hash_value}"
