# Smart File Organizer

A modular desktop application that safely organizes messy folders by file type, custom rules, and modification date. It includes preview mode, duplicate detection, activity history, and undo support.

## Features

- Categorizes images, documents, audio, video, archives, code, and unknown files.
- Preview changes before any files move.
- Never overwrites an existing file; it creates a numbered name instead.
- Skips the generated `Organized/` folder to avoid recursive processing.
- Optional year/month date-based destinations.
- SHA-256 duplicate detection that reports matches without deleting files.
- SQLite-backed operation history and one-click undo.
- Custom extension-to-category rules in Settings.

## Setup

```bash
cd Smart-File-Organizer
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

Choose **Organize Files**, select a test folder, review the preview, then click **Organize files**. The application asks for confirmation before moving anything. The SQLite history database is created as `organizer.db` next to `main.py`.

## Run tests

```bash
python -m unittest discover -s tests -v
```

## Project structure

```text
Smart-File-Organizer/
├── main.py
├── organizer.py          # Planning and executing safe file moves
├── file_detector.py      # Built-in and custom categorization rules
├── duplicate_checker.py  # SHA-256 duplicate groups
├── database.py           # SQLite schema and persistence
├── undo_manager.py       # Restore completed batches
├── gui/
│   ├── app.py
│   ├── dashboard.py
│   ├── history.py
│   └── settings.py
└── tests/
    └── test_organizer.py
```

## Safety notes

This project moves files only after explicit confirmation. It does not delete duplicates. Test with a copy of sample files first, and keep backups of important data.
