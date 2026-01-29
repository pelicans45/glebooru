from datetime import datetime, UTC
import threading
from typing import Any, Dict, List


class LruCacheItem:
    def __init__(self, key: object, value: Any) -> None:
        self.key = key
        self.value = value
        self.timestamp = datetime.now(UTC).replace(tzinfo=None)


class LruCache:
    def __init__(self, length: int) -> None:
        self.length = length
        self.hash = {}  # type: Dict[object, LruCacheItem]
        self.item_list = []  # type: List[LruCacheItem]
        self._lock = threading.RLock()

    def insert_item(self, item: LruCacheItem) -> None:
        with self._lock:
            if item.key in self.hash:
                old_item = self.hash[item.key]
                try:
                    self.item_list.remove(old_item)
                except ValueError:
                    pass
            self.hash[item.key] = item
            self.item_list.insert(0, item)
            while len(self.item_list) > self.length:
                self.remove_item(self.item_list[-1], locked=True)

    def remove_all(self) -> None:
        with self._lock:
            self.hash = {}
            self.item_list = []

    def remove_item(self, item: LruCacheItem, locked: bool = False) -> None:
        if not locked:
            self._lock.acquire()
        try:
            if item.key in self.hash:
                del self.hash[item.key]
            try:
                self.item_list.remove(item)
            except ValueError:
                pass
        finally:
            if not locked:
                self._lock.release()

    def remove_key(self, key: object) -> None:
        with self._lock:
            item = self.hash.get(key)
            if item:
                self.remove_item(item, locked=True)


_CACHE = LruCache(length=100)


def purge() -> None:
    _CACHE.remove_all()


def has(key: object) -> bool:
    with _CACHE._lock:
        return key in _CACHE.hash


def get(key: object) -> Any:
    with _CACHE._lock:
        item = _CACHE.hash.get(key)
        if not item:
            return None
        return item.value


def remove(key: object) -> None:
    _CACHE.remove_key(key)


def put(key: object, value: Any) -> None:
    _CACHE.insert_item(LruCacheItem(key, value))
