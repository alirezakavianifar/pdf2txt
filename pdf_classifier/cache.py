"""
Caching Module for Template Detection

Implements caching for performance optimization.
"""

from pathlib import Path
from typing import Optional, Dict, Any
import hashlib


class DetectionCache:
    """Cache for detection results and intermediate data."""
    
    def __init__(self, cache_dir: Optional[Path] = None):
        # In-memory caches only (no disk cache for portability)
        self._image_cache: Dict[str, Any] = {}
        self._region_cache: Dict[str, Any] = {}
        self._hash_cache: Dict[str, Any] = {}
        self._template_db_cache: Optional[Dict] = None
    
    def get_cache_key(self, pdf_path: Path, suffix: str = "") -> str:
        """Generate cache key from PDF path."""
        # Use file path and modification time
        try:
            stat = pdf_path.stat()
            key_data = f"{pdf_path}_{stat.st_mtime}_{suffix}"
        except Exception:
            key_data = f"{pdf_path}_{suffix}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get_cached_image(self, pdf_path: Path) -> Optional[Any]:
        """Get cached rendered image."""
        cache_key = self.get_cache_key(pdf_path, "image")
        return self._image_cache.get(cache_key)
    
    def cache_image(self, pdf_path: Path, image_data: Any):
        """Cache rendered image."""
        cache_key = self.get_cache_key(pdf_path, "image")
        self._image_cache[cache_key] = image_data
    
    def get_cached_regions(self, pdf_path: Path) -> Optional[Dict]:
        """Get cached extracted regions."""
        cache_key = self.get_cache_key(pdf_path, "regions")
        return self._region_cache.get(cache_key)
    
    def cache_regions(self, pdf_path: Path, regions: Dict):
        """Cache extracted regions."""
        cache_key = self.get_cache_key(pdf_path, "regions")
        self._region_cache[cache_key] = regions
    
    def get_cached_hashes(self, image_key: str) -> Optional[Dict]:
        """Get cached hash calculations."""
        return self._hash_cache.get(image_key)
    
    def cache_hashes(self, image_key: str, hashes: Dict):
        """Cache hash calculations."""
        self._hash_cache[image_key] = hashes
    
    def get_template_db(self) -> Optional[Dict]:
        """Get cached template database."""
        return self._template_db_cache
    
    def cache_template_db(self, templates_db: Dict):
        """Cache template database."""
        self._template_db_cache = templates_db
    
    def clear(self):
        """Clear all caches."""
        self._image_cache.clear()
        self._region_cache.clear()
        self._hash_cache.clear()
        self._template_db_cache = None


# Global cache instance
_global_cache = DetectionCache()


def get_cache() -> DetectionCache:
    """Get global cache instance."""
    return _global_cache

