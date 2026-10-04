from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
from typing import Callable, Iterable

from file_detector import FileDetector


@dataclass(frozen=True)
class FileOperation:
    source: Path
    destination: Path
    category: str


class FileOrganizer:
    """Plan and execute safe file moves for a selected directory."""

    def __init__(self, detector: FileDetector | None = None) -> None:
        self.detector = detector or FileDetector()

    def plan(self, folder_path: str | Path, *, date_based: bool = False) -> list[FileOperation]:
        folder = Path(folder_path).expanduser().resolve()
        if not folder.is_dir():
            raise NotADirectoryError(f"Invalid folder path: {folder}")

        output_root = folder / "Organized"
        operations: list[FileOperation] = []
        for source in sorted(folder.iterdir(), key=lambda p: p.name.lower()):
            if not source.is_file() or output_root in source.parents:
                continue
            category = self.detector.category_for(source)
            destination_dir = output_root / category
            if date_based:
                modified = self.detector.modified_datetime(source)
                destination_dir = destination_dir / str(modified.year) / modified.strftime("%B")
            destination = self._unique_destination(destination_dir / source.name)
            operations.append(FileOperation(source, destination, category))
        return operations

    def execute(
        self,
        operations: Iterable[FileOperation],
        *,
        progress_callback: Callable[[FileOperation], None] | None = None,
    ) -> list[FileOperation]:
        completed: list[FileOperation] = []
        for operation in operations:
            operation.destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(operation.source), str(operation.destination))
            completed.append(operation)
            if progress_callback:
                progress_callback(operation)
        return completed

    @staticmethod
    def _unique_destination(candidate: Path) -> Path:
        if not candidate.exists():
            return candidate
        counter = 1
        while True:
            alternate = candidate.with_name(f"{candidate.stem}_{counter}{candidate.suffix}")
            if not alternate.exists():
                return alternate
            counter += 1
