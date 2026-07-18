"""
Cache service wrapper for Catalyst Cache operations with JSON serialization.
"""

import json
import hashlib
import os
from typing import Optional, Any
from datetime import datetime


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle datetime objects."""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class CacheService:
    """Wrapper for Catalyst Cache operations with JSON serialization."""
    
    def __init__(self, segment_service, max_cache_size_kb: int = 100):
        self.segment = segment_service
        self.disabled = os.getenv("DISABLE_CACHE", "false").lower() == "true"
        self.max_cache_size_bytes = max_cache_size_kb * 1024
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value and deserialize JSON."""
        if self.disabled:
            return None
        try:
            result = self.segment.get(key)
            if result is None:
                return None
            if result and 'cache_value' in result:
                cache_value = result['cache_value']
                if cache_value is None:
                    return None
                return json.loads(cache_value)
            return None
        except Exception as e:
            print(f"[Cache] Get error for key {key}: {e}")
            return None
    
    def put(self, key: str, value: Any, expiry_in_hours: int = 48) -> bool:
        """Cache value with JSON serialization."""
        if self.disabled:
            return False
        try:
            json_value = json.dumps(value, cls=DateTimeEncoder)
            
            # Check if value size exceeds limit
            value_size = len(json_value.encode('utf-8'))
            size_kb = value_size / 1024
            if value_size > self.max_cache_size_bytes:
                max_kb = self.max_cache_size_bytes / 1024
                print(f"[Cache] Skip caching {key}: value size {size_kb:.2f}KB exceeds limit {max_kb}KB")
                return False
            
            self.segment.put(key, json_value, expiry_in_hours)
            print(f"[Cache] Put success for key: {key} ({size_kb:.2f}KB)")
            return True
        except Exception as e:
            print(f"[Cache] Put error for key {key}: {e}")
            return False
    
    def update(self, key: str, value: Any, expiry_in_hours: int = 48) -> bool:
        """Update cached value with JSON serialization."""
        if self.disabled:
            return False
        try:
            json_value = json.dumps(value, cls=DateTimeEncoder)
            
            # Check if value size exceeds limit
            value_size = len(json_value.encode('utf-8'))
            size_kb = value_size / 1024
            if value_size > self.max_cache_size_bytes:
                max_kb = self.max_cache_size_bytes / 1024
                print(f"[Cache] Skip updating {key}: value size {size_kb:.2f}KB exceeds limit {max_kb}KB")
                return False
            
            self.segment.update(key, json_value, expiry_in_hours)
            print(f"[Cache] Update success for key: {key} ({size_kb:.2f}KB)")
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
    
    def flush_all(self) -> bool:
        """Flush all cached values in the segment."""
        if self.disabled:
            return False
        try:
            # Catalyst Cache doesn't have a direct flush method
            # We need to get all keys and delete them one by one
            # For now, we'll log this as a limitation
            print(f"[Cache] Flush all - Catalyst Cache doesn't support direct flush")
            print(f"[Cache] To clear cache, use the Catalyst console or delete individual keys")
            return False
        except Exception as e:
            print(f"[Cache] Flush all error: {e}")
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
        Formatted cache key with shortened MD5 hash
    """
    key_string = ":".join(str(arg) for arg in args)
    hash_value = hashlib.md5(key_string.encode()).hexdigest()
    # Use first 12 characters of hash to avoid cache key length limits
    short_hash = hash_value[:12]
    return f"{prefix}:{short_hash}"
