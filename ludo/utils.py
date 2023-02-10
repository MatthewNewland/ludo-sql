import os
from pathlib import Path
import pickle
from typing import Any
from starlite.config.cache import SimpleCacheBackend


class PicklingCacheBackend(SimpleCacheBackend):
    def __init__(self, path: os.PathLike) -> None:
        super().__init__()
        self.path = Path(path)
        if self.path.exists():
            self._store = pickle.loads(self.path.read_bytes())

    async def write_to_disk(self):
        async with self._lock:
            self.path.write_bytes(pickle.dumps(self._store))

    async def set(self, key: str, value: Any, expiration: int) -> None:
        await super().set(key, value, expiration)
        await self.write_to_disk()

    async def delete(self, key: str) -> None:
        await super().delete(key)
        await self.write_to_disk()
