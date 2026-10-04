from __future__ import annotations

from datetime import datetime
from pathlib import Path


DEFAULT_FILE_TYPES: dict[str, set[str]] = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp", ".bmp", ".tiff"},
    "Documents": {".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".ppt", ".pptx", ".xls", ".xlsx"},
    "Videos": {".mp4", ".mkv", ".mov", ".avi", ".webm", ".flv", ".wmv"},
    "Audio": {".mp3", ".wav", ".aac", ".flac", ".ogg", ".m4a", ".wma"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"},
    "Code": {".py", ".js", ".ts", ".java", ".c", ".cpp", ".html", ".css", ".json", ".sql"},
}


class FileDetector:
    def __init__(self, custom_rules: dict[str, str] | None = None) -> None:
        self.custom_rules = {suffix.lower(): category for suffix, category in (custom_rules or {}).items()}

    def category_for(self, file_path: str | Path) -> str:
        path = Path(file_path)
        suffix = path.suffix.lower()
        if suffix in self.custom_rules:
            return self.custom_rules[suffix]
        for category, extensions in DEFAULT_FILE_TYPES.items():
            if suffix in extensions:
                return category
        return "Others"

    @staticmethod
    def modified_datetime(file_path: str | Path) -> datetime:
        return datetime.fromtimestamp(Path(file_path).stat().st_mtime)
