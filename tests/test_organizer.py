import tempfile
import unittest
from pathlib import Path

from database import Database
from duplicate_checker import DuplicateChecker
from file_detector import FileDetector
from organizer import FileOrganizer
from undo_manager import UndoManager


class SmartFileOrganizerTests(unittest.TestCase):
    def test_plan_classifies_and_skips_organized(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            (folder / "photo.PNG").write_text("image")
            (folder / "notes.txt").write_text("notes")
            (folder / "Organized").mkdir()
            (folder / "Organized" / "old.pdf").write_text("old")
            operations = FileOrganizer().plan(folder)
            self.assertEqual(sorted(item.category for item in operations), ["Documents", "Images"])

    def test_execute_avoids_overwriting(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            (folder / "a.txt").write_text("one")
            destination = folder / "Organized" / "Documents"
            destination.mkdir(parents=True)
            (destination / "a.txt").write_text("existing")
            completed = FileOrganizer().execute(FileOrganizer().plan(folder))
            self.assertEqual(completed[0].destination.name, "a_1.txt")
            self.assertTrue((destination / "a_1.txt").exists())

    def test_duplicates_are_content_based(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            (folder / "one.bin").write_bytes(b"same")
            (folder / "two.bin").write_bytes(b"same")
            duplicate_groups = DuplicateChecker().find_duplicates(folder)
            self.assertEqual(len(duplicate_groups), 1)
            self.assertEqual(len(next(iter(duplicate_groups.values()))), 2)

    def test_database_and_undo(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            source = folder / "file.txt"
            source.write_text("hello")
            database = Database(Path(temp).parent / "smart-file-organizer-test.db")
            operation = FileOrganizer().plan(folder)
            completed = FileOrganizer().execute(operation)
            batch = "test-batch"
            database.record_operations(batch, [(str(completed[0].source), str(completed[0].destination), completed[0].category)])
            self.assertEqual(UndoManager(database).undo(batch), 1)
            self.assertTrue(source.exists())

    def test_invalid_folder(self):
        with self.assertRaises(NotADirectoryError):
            FileOrganizer().plan("/path/that/does/not/exist")


if __name__ == "__main__":
    unittest.main()
