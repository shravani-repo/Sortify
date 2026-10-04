from __future__ import annotations

from collections import Counter
from pathlib import Path
from uuid import uuid4

import customtkinter as ctk
from tkinter import filedialog, messagebox

from database import Database
from file_detector import FileDetector
from organizer import FileOrganizer
from undo_manager import UndoManager
from gui.dashboard import DashboardFrame
from gui.history import HistoryFrame
from gui.settings import SettingsFrame
from gui.theme import setup_theme


class OrganizerView(ctk.CTkFrame):
    def __init__(self, master, app, **kwargs):
        super().__init__(master, **kwargs)

        self.app = app
        self.folder = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)

        # ---------------------------------------------------------
        # Header
        # ---------------------------------------------------------

        ctk.CTkLabel(
            self,
            text="Organize Files",
            font=ctk.CTkFont(size=30, weight="bold")
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=24,
            pady=(24, 2)
        )

        ctk.CTkLabel(
            self,
            text="Select a folder and safely organize your files",
            text_color="gray60"
        ).grid(
            row=1,
            column=0,
            sticky="w",
            padx=24,
            pady=(0, 18)
        )

        # ---------------------------------------------------------
        # Folder selection card
        # ---------------------------------------------------------

        folder_card = ctk.CTkFrame(
            self,
            corner_radius=14
        )

        folder_card.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=20,
            pady=6
        )

        ctk.CTkLabel(
            folder_card,
            text="Selected Folder",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(
            anchor="w",
            padx=18,
            pady=(14, 2)
        )

        self.path_label = ctk.CTkLabel(
            folder_card,
            text="No folder selected",
            anchor="w",
            text_color="gray60"
        )

        self.path_label.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(18, 8),
            pady=(0, 14)
        )

        ctk.CTkButton(
            folder_card,
            text="Browse",
            width=100,
            command=self.choose_folder
        ).pack(
            side="right",
            padx=18,
            pady=(8, 14)
        )

        # ---------------------------------------------------------
        # Options + actions
        # ---------------------------------------------------------

        controls = ctk.CTkFrame(
            self,
            corner_radius=14
        )

        controls.grid(
            row=3,
            column=0,
            sticky="ew",
            padx=20,
            pady=6
        )

        options_frame = ctk.CTkFrame(
            controls,
            fg_color="transparent"
        )

        options_frame.pack(
            side="left",
            fill="x",
            expand=True,
            padx=18,
            pady=14
        )

        ctk.CTkLabel(
            options_frame,
            text="Organization Options",
            font=ctk.CTkFont(size=15, weight="bold")
        ).pack(anchor="w")

        self.date_based = ctk.CTkCheckBox(
            options_frame,
            text="Organize inside year/month folders"
        )

        self.date_based.pack(
            anchor="w",
            pady=(8, 0)
        )

        buttons = ctk.CTkFrame(
            controls,
            fg_color="transparent"
        )

        buttons.pack(
            side="right",
            padx=18,
            pady=14
        )

        ctk.CTkButton(
            buttons,
            text="Preview",
            width=100,
            command=self.preview
        ).pack(
            side="left",
            padx=4
        )

        ctk.CTkButton(
            buttons,
            text="Organize",
            width=110,
            fg_color="#2e8b57",
            hover_color="#246b45",
            command=self.organize
        ).pack(
            side="left",
            padx=4
        )

        # ---------------------------------------------------------
        # Preview section
        # ---------------------------------------------------------

        preview_card = ctk.CTkFrame(
            self,
            corner_radius=14
        )

        preview_card.grid(
            row=4,
            column=0,
            sticky="nsew",
            padx=20,
            pady=(8, 6)
        )

        preview_card.grid_columnconfigure(
            0,
            weight=1
        )

        preview_card.grid_rowconfigure(
            1,
            weight=1
        )

        preview_header = ctk.CTkFrame(
            preview_card,
            fg_color="transparent"
        )

        preview_header.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=18,
            pady=(14, 6)
        )

        ctk.CTkLabel(
            preview_header,
            text="Organization Preview",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left")

        self.progress_label = ctk.CTkLabel(
            preview_header,
            text="0 / 0 files",
            text_color="gray60"
        )

        self.progress_label.pack(side="right")

        self.preview_box = ctk.CTkTextbox(
            preview_card
        )

        self.preview_box.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=18,
            pady=(4, 14)
        )

        # ---------------------------------------------------------
        # Progress + status
        # ---------------------------------------------------------

        status_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        status_frame.grid(
            row=5,
            column=0,
            sticky="ew",
            padx=24,
            pady=(4, 14)
        )

        self.progress = ctk.CTkProgressBar(
            status_frame
        )

        self.progress.pack(
            fill="x",
            pady=(0, 5)
        )

        self.progress.set(0)

        self.log_label = ctk.CTkLabel(
            status_frame,
            text="Ready",
            anchor="w",
            text_color="gray60"
        )

        self.log_label.pack(fill="x")

    # =============================================================
    # Folder Selection
    # =============================================================

    def choose_folder(self):
        selected = filedialog.askdirectory(
            title="Choose a folder to organize"
        )

        if not selected:
            return

        self.folder = Path(selected)

        self.path_label.configure(
            text=str(self.folder),
            text_color=("gray10", "gray90")
        )

        self.preview()

        self.app.refresh_dashboard(
            self.folder
        )

    # =============================================================
    # Get Operations
    # =============================================================

    def get_operations(self):
        if not self.folder:
            messagebox.showinfo(
                "Choose a folder",
                "Select a folder before continuing."
            )
            return []

        detector = FileDetector(
            self.app.database.get_rules()
        )

        return FileOrganizer(detector).plan(
            self.folder,
            date_based=bool(
                self.date_based.get()
            )
        )

    # =============================================================
    # Preview
    # =============================================================

    def preview(self):
        operations = self.get_operations()

        self.preview_box.delete(
            "1.0",
            "end"
        )

        if not operations:
            self.progress.set(0)

            self.progress_label.configure(
                text="0 / 0 files"
            )

            self.log_label.configure(
                text="No files available for organization."
            )

            self.preview_box.insert(
                "end",
                "No files found to organize."
            )

            return

        for operation in operations:
            self.preview_box.insert(
                "end",
                f"{operation.source.name}\n"
                f"    → {operation.destination.relative_to(self.folder)}\n\n"
            )

        self.progress.set(0)

        self.progress_label.configure(
            text=f"0 / {len(operations)} files"
        )

        self.log_label.configure(
            text=(
                f"Preview ready: {len(operations)} file(s) "
                "will be moved. No changes made."
            )
        )

    # =============================================================
    # Progress
    # =============================================================

    def update_progress(
        self,
        operation,
        completed,
        total
    ):
        percentage = completed / total

        self.progress.set(
            percentage
        )

        self.progress_label.configure(
            text=f"{completed} / {total} files"
        )

        self.log_label.configure(
            text=f"Organizing: {operation.source.name}"
        )

        self.update_idletasks()

    # =============================================================
    # Organize
    # =============================================================

    def organize(self):
        operations = self.get_operations()

        if not operations:
            return

        confirm = messagebox.askyesno(
            "Confirm organization",
            f"Move {len(operations)} file(s) into Organized/?"
        )

        if not confirm:
            return

        self.progress.set(0)

        self.progress_label.configure(
            text=f"0 / {len(operations)} files"
        )

        self.log_label.configure(
            text="Starting organization..."
        )

        organizer = FileOrganizer(
            FileDetector(
                self.app.database.get_rules()
            )
        )

        total = len(operations)
        completed_count = 0

        def progress_callback(operation):
            nonlocal completed_count

            completed_count += 1

            self.update_progress(
                operation,
                completed_count,
                total
            )

        completed = organizer.execute(
            operations,
            progress_callback=progress_callback
        )

        self.progress.set(1)

        self.progress_label.configure(
            text=f"{len(completed)} / {total} files"
        )

        batch_id = str(uuid4())

        self.app.database.record_operations(
            batch_id,
            [
                (
                    str(item.source),
                    str(item.destination),
                    item.category
                )
                for item in completed
            ]
        )

        self.log_label.configure(
            text=(
                f"Completed successfully: "
                f"{len(completed)} file(s) moved."
            )
        )

        self.app.refresh_dashboard(
            self.folder
        )

        self.app.history.refresh()

        self.show_summary(
            completed
        )

    # =============================================================
    # Organization Summary
    # =============================================================

    def show_summary(self, completed):
        summary_window = ctk.CTkToplevel(self)

        summary_window.title(
            "Organization Complete"
        )

        summary_window.geometry(
            "480x500"
        )

        summary_window.resizable(
            False,
            False
        )

        # ---------------------------------------------------------
        # Header
        # ---------------------------------------------------------

        ctk.CTkLabel(
            summary_window,
            text="Organization Complete",
            font=ctk.CTkFont(
                size=26,
                weight="bold"
            )
        ).pack(
            pady=(30, 6)
        )

        ctk.CTkLabel(
            summary_window,
            text="Your files have been organized successfully.",
            text_color="gray60"
        ).pack(
            pady=(0, 20)
        )

        # ---------------------------------------------------------
        # Total files
        # ---------------------------------------------------------

        total_card = ctk.CTkFrame(
            summary_window,
            corner_radius=14
        )

        total_card.pack(
            fill="x",
            padx=30,
            pady=8
        )

        ctk.CTkLabel(
            total_card,
            text="Files Organized",
            font=ctk.CTkFont(
                size=15,
                weight="bold"
            )
        ).pack(
            anchor="w",
            padx=20,
            pady=(16, 2)
        )

        ctk.CTkLabel(
            total_card,
            text=str(len(completed)),
            font=ctk.CTkFont(
                size=30,
                weight="bold"
            )
        ).pack(
            anchor="w",
            padx=20,
            pady=(0, 16)
        )

        # ---------------------------------------------------------
        # Category summary
        # ---------------------------------------------------------

        categories = Counter(
            operation.category
            for operation in completed
        )

        category_card = ctk.CTkFrame(
            summary_window,
            corner_radius=14
        )

        category_card.pack(
            fill="x",
            padx=30,
            pady=8
        )

        ctk.CTkLabel(
            category_card,
            text="Category Breakdown",
            font=ctk.CTkFont(
                size=15,
                weight="bold"
            )
        ).pack(
            anchor="w",
            padx=20,
            pady=(16, 8)
        )

        for category, count in sorted(
            categories.items()
        ):
            row = ctk.CTkFrame(
                category_card,
                fg_color="transparent"
            )

            row.pack(
                fill="x",
                padx=20,
                pady=3
            )

            ctk.CTkLabel(
                row,
                text=category
            ).pack(
                side="left"
            )

            ctk.CTkLabel(
                row,
                text=str(count),
                font=ctk.CTkFont(
                    weight="bold"
                )
            ).pack(
                side="right"
            )

        # ---------------------------------------------------------
        # Close button
        # ---------------------------------------------------------

        ctk.CTkButton(
            summary_window,
            text="Done",
            width=140,
            height=40,
            command=summary_window.destroy
        ).pack(
            pady=24
        )

        summary_window.transient(
            self.winfo_toplevel()
        )

        summary_window.grab_set()


class SmartFileOrganizerApp(ctk.CTk):
    def __init__(self):
        setup_theme()

        super().__init__()

        # =========================================================
        # Sortify App Identity
        # =========================================================

        self.title(
            "Sortify"
        )

        self.geometry(
            "1100x700"
        )

        self.minsize(
            850,
            550
        )

        self.database = Database(
            Path(__file__).resolve().parent.parent
            / "organizer.db"
        )

        self.undo_manager = UndoManager(
            self.database
        )

        # =========================================================
        # Main window layout
        # =========================================================

        self.grid_columnconfigure(
            1,
            weight=1
        )

        self.grid_rowconfigure(
            0,
            weight=1
        )

        # =========================================================
        # Sidebar
        # =========================================================

        self.sidebar = ctk.CTkFrame(
            self,
            width=220,
            corner_radius=0
        )

        self.sidebar.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        self.sidebar.grid_propagate(
            False
        )

        # ---------------------------------------------------------
        # Sortify Logo / Title
        # ---------------------------------------------------------
        ctk.CTkLabel(
            self.sidebar,
            text="Sortify",
            font=ctk.CTkFont(
                size=28,
                weight="bold"
            )
        ).pack(
            pady=(36, 8)
        )

        ctk.CTkLabel(
            self.sidebar,
            text="SMART FILE MANAGEMENT",
            font=ctk.CTkFont(
                size=10,
                weight="bold"
            ),
            text_color="gray60"
        ).pack(
            pady=(0, 4)
        )

        ctk.CTkLabel(
            self.sidebar,
            text="Smart. Simple. Sorted.",
            font=ctk.CTkFont(
                size=11
            ),
            text_color="gray60"
        ).pack(
            pady=(0, 26)
        )
        # =========================================================
        # Navigation
        # =========================================================

        self.nav_buttons = {}

        navigation = (
            ("Dashboard", self.dashboard_callback),
            ("Organize Files", self.organizer_callback),
            ("History", self.history_callback),
            ("Settings", self.settings_callback),
        )

        for label, callback in navigation:
            button = ctk.CTkButton(
                self.sidebar,
                text=label,
                anchor="w",
                height=42,
                corner_radius=8,
                fg_color="transparent",
                hover_color=("gray80", "gray25"),
                command=callback
            )

            button.pack(
                fill="x",
                padx=14,
                pady=4
            )

            self.nav_buttons[label] = button

        # =========================================================
        # Sidebar Footer
        # =========================================================

        footer = ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent"
        )

        footer.pack(
            side="bottom",
            fill="x",
            padx=14,
            pady=20
        )

        ctk.CTkLabel(
            footer,
            text="Safe preview mode",
            font=ctk.CTkFont(
                size=12,
                weight="bold"
            )
        ).pack(
            anchor="w"
        )

        ctk.CTkLabel(
            footer,
            text="No files are deleted",
            text_color="gray60",
            font=ctk.CTkFont(size=11)
        ).pack(
            anchor="w"
        )

        ctk.CTkLabel(
            footer,
            text="v1.0 • Sortify",
            text_color="gray60",
            font=ctk.CTkFont(size=10)
        ).pack(
            anchor="w",
            pady=(10, 0)
        )

        # =========================================================
        # Main Content
        # =========================================================

        self.content = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        self.content.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=8,
            pady=8
        )

        self.content.grid_rowconfigure(
            0,
            weight=1
        )

        self.content.grid_columnconfigure(
            0,
            weight=1
        )

        # =========================================================
        # Pages
        # =========================================================

        self.dashboard = DashboardFrame(
            self.content,
            self.organize_from_dashboard
        )

        self.organizer = OrganizerView(
            self.content,
            self
        )

        self.history = HistoryFrame(
            self.content,
            self.database,
            self.undo_manager,
            self.refresh_current
        )

        self.settings = SettingsFrame(
            self.content,
            self.database,
            self.refresh_rules
        )

        self.show(
            self.dashboard
        )

    # =============================================================
    # Sidebar Callbacks
    # =============================================================

    def dashboard_callback(self):
        self.show(
            self.dashboard,
            "Dashboard"
        )

    def organizer_callback(self):
        self.show(
            self.organizer,
            "Organize Files"
        )

    def history_callback(self):
        self.show(
            self.history,
            "History"
        )

    def settings_callback(self):
        self.show(
            self.settings,
            "Settings"
        )

    # =============================================================
    # Navigation
    # =============================================================

    def show(self, frame, active_name=None):
        for child in (
            self.dashboard,
            self.organizer,
            self.history,
            self.settings
        ):
            child.grid_forget()

        frame.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        if active_name:
            self.update_active_navigation(
                active_name
            )

        # Refresh dashboard whenever it is opened
        if frame is self.dashboard:
            if self.organizer.folder:
                self.refresh_dashboard(
                    self.organizer.folder
                )

        if frame is self.history:
            self.history.refresh()

        if frame is self.settings:
            self.settings.refresh()

    def update_active_navigation(self, active_name):
        for name, button in self.nav_buttons.items():
            if name == active_name:
                button.configure(
                    fg_color=("#d9e9ff", "#1f538d"),
                    text_color=("gray10", "white")
                )
            else:
                button.configure(
                    fg_color="transparent",
                    text_color=("gray10", "gray90")
                )

    def organize_from_dashboard(self):
        self.organizer_callback()

    # =============================================================
    # Refresh
    # =============================================================

    def refresh_rules(self):
        if self.organizer.folder:
            self.organizer.preview()

    def refresh_current(self):
        if self.organizer.folder:
            self.refresh_dashboard(
                self.organizer.folder
            )

    # =============================================================
    # Dashboard Statistics
    # =============================================================

    def refresh_dashboard(
        self,
        folder: Path
    ):
        try:
            detector = FileDetector(
                self.database.get_rules()
            )

            files = []

            # Count files directly inside the selected folder
            for path in folder.iterdir():

                if path.is_file():
                    files.append(path)

                # Also count files inside Organized/
                elif (
                    path.is_dir()
                    and path.name == "Organized"
                ):
                    for organized_file in path.rglob("*"):
                        if organized_file.is_file():
                            files.append(organized_file)

            counts = Counter(
                detector.category_for(path)
                for path in files
            )

            # =====================================================
            # Dashboard Statistics
            # =====================================================

            stats = {
                "total": len(files),
                "Images": counts["Images"],
                "Documents": counts["Documents"],
                "media": (
                    counts["Audio"]
                    + counts["Videos"]
                ),
                "categories": dict(counts)
            }

            self.dashboard.update_stats(
                stats
            )

        except OSError:
            pass