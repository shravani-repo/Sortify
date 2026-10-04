from __future__ import annotations

from collections import defaultdict
from hashlib import sha256
from pathlib import Path
from typing import Iterable


class DuplicateChecker:
    """Find duplicate files by content without deleting anything."""

    def find_duplicates(self, folder_path: str | Path, *, include_subfolders: bool = True) -> dict[str, list[Path]]:
        folder = Path(folder_path).expanduser().resolve()
        files = folder.rglob("*") if include_subfolders else folder.iterdir()
        by_size: dict[int, list[Path]] = defaultdict(list)
        for path in files:
            if path.is_file():
                try:
                    by_size[path.stat().st_size].append(path)
                except OSError:
                    continue

        duplicates: dict[str, list[Path]] = {}
        for candidates in by_size.values():
            if len(candidates) < 2:
                continue
            by_hash: dict[str, list[Path]] = defaultdict(list)
            for path in candidates:
                try:
                    by_hash[self._hash_file(path)].append(path)
                except OSError:
                    continue
            duplicates.update({digest: paths for digest, paths in by_hash.items() if len(paths) > 1})
        return duplicates

    @staticmethod
    def _hash_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
        digest = sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(chunk_size), b""):
                digest.update(chunk)
        return digest.hexdigest()
