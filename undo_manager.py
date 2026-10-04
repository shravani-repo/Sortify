from __future__ import annotations

from pathlib import Path
import shutil

from database import Database


class UndoManager:
    def __init__(self, database: Database) -> None:
        self.database = database

    def undo(self, batch_id: str) -> int:
        rows = self.database.get_batch(batch_id)

        if not rows:
            return 0

        # Prevent undoing the same batch twice
        if rows[0]["undone"]:
            return 0

        restored = 0

        for row in reversed(rows):
            source = Path(row["source_path"])
            destination = Path(row["destination_path"])

            # If the organized file no longer exists, skip it safely
            if not destination.exists():
                continue

            # Make sure the original folder exists
            source.parent.mkdir(parents=True, exist_ok=True)

            # Don't overwrite an existing file
            if source.exists():
                source = source.with_name(
                    f"{source.stem}_restored{source.suffix}"
                )

            try:
                shutil.move(str(destination), str(source))
                restored += 1
            except OSError:
                # If one file cannot be restored, continue with the others
                continue

        self.database.mark_batch_undone(batch_id)

        return restored