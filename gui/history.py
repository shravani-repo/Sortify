from __future__ import annotations

import customtkinter as ctk
from tkinter import messagebox


class HistoryFrame(ctk.CTkFrame):
    def __init__(
        self,
        master,
        database,
        undo_manager,
        refresh_callback,
        **kwargs
    ):
        super().__init__(master, **kwargs)

        self.database = database
        self.undo_manager = undo_manager
        self.refresh_callback = refresh_callback

        # Current filters
        self.search_text = ""
        self.status_filter = "All"

        # =========================================================
        # Header
        # =========================================================

        ctk.CTkLabel(
            self,
            text="History",
            font=ctk.CTkFont(
                size=30,
                weight="bold"
            )
        ).pack(
            anchor="w",
            padx=24,
            pady=(24, 4)
        )

        ctk.CTkLabel(
            self,
            text="View your previous file organization batches",
            text_color="gray60"
        ).pack(
            anchor="w",
            padx=24,
            pady=(0, 18)
        )

        # =========================================================
        # Search + Filter Bar
        # =========================================================

        filter_frame = ctk.CTkFrame(
            self,
            corner_radius=12
        )

        filter_frame.pack(
            fill="x",
            padx=24,
            pady=(0, 12)
        )

        self.search_entry = ctk.CTkEntry(
            filter_frame,
            placeholder_text="Search by date or batch ID..."
        )

        self.search_entry.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(14, 8),
            pady=14
        )

        self.search_entry.bind(
            "<KeyRelease>",
            self.on_search
        )

        self.status_menu = ctk.CTkOptionMenu(
            filter_frame,
            values=[
                "All",
                "Completed",
                "Undone"
            ],
            command=self.on_status_filter
        )

        self.status_menu.pack(
            side="left",
            padx=8,
            pady=14
        )

        ctk.CTkButton(
            filter_frame,
            text="Clear",
            width=80,
            command=self.clear_filters
        ).pack(
            side="left",
            padx=(8, 14),
            pady=14
        )

        # =========================================================
        # History Area
        # =========================================================

        self.history_frame = ctk.CTkScrollableFrame(
            self,
            corner_radius=12
        )

        self.history_frame.pack(
            fill="both",
            expand=True,
            padx=24,
            pady=8
        )

        self.refresh()

    # =============================================================
    # Search
    # =============================================================

    def on_search(self, event=None):
        self.search_text = (
            self.search_entry.get()
            .strip()
            .lower()
        )

        self.refresh()

    # =============================================================
    # Status Filter
    # =============================================================

    def on_status_filter(self, value):
        self.status_filter = value
        self.refresh()

    # =============================================================
    # Clear Filters
    # =============================================================

    def clear_filters(self):
        self.search_entry.delete(
            0,
            "end"
        )

        self.status_menu.set(
            "All"
        )

        self.search_text = ""
        self.status_filter = "All"

        self.refresh()

    # =============================================================
    # Refresh
    # =============================================================

    def refresh(self):
        for widget in self.history_frame.winfo_children():
            widget.destroy()

        batches = self.database.list_batches()

        # ---------------------------------------------------------
        # Apply filters
        # ---------------------------------------------------------

        filtered_batches = []

        for row in batches:

            # Status filter
            if self.status_filter == "Completed":
                if row["undone"]:
                    continue

            elif self.status_filter == "Undone":
                if not row["undone"]:
                    continue

            # Search filter
            if self.search_text:

                searchable_text = (
                    f"{row['batch_id']} "
                    f"{row['created_at']} "
                    f"{row['file_count']}"
                ).lower()

                if self.search_text not in searchable_text:
                    continue

            filtered_batches.append(row)

        # ---------------------------------------------------------
        # No results
        # ---------------------------------------------------------

        if not filtered_batches:

            empty_frame = ctk.CTkFrame(
                self.history_frame,
                fg_color="transparent"
            )

            empty_frame.pack(
                fill="both",
                expand=True,
                pady=60
            )

            if batches:
                title = "No matching history"
                description = (
                    "Try changing your search or filter."
                )
            else:
                title = "No organization history yet"
                description = (
                    "Your completed organization batches "
                    "will appear here."
                )

            ctk.CTkLabel(
                empty_frame,
                text=title,
                font=ctk.CTkFont(
                    size=20,
                    weight="bold"
                )
            ).pack(
                pady=(20, 6)
            )

            ctk.CTkLabel(
                empty_frame,
                text=description,
                text_color="gray60"
            ).pack()

            return

        # ---------------------------------------------------------
        # Display results
        # ---------------------------------------------------------

        for index, row in enumerate(
            filtered_batches,
            1
        ):
            self.create_history_card(
                index,
                row
            )

    # =============================================================
    # History Card
    # =============================================================

    def create_history_card(
        self,
        index,
        row
    ):
        card = ctk.CTkFrame(
            self.history_frame,
            corner_radius=12
        )

        card.pack(
            fill="x",
            padx=4,
            pady=6
        )

        info = ctk.CTkFrame(
            card,
            fg_color="transparent"
        )

        info.pack(
            side="left",
            fill="x",
            expand=True,
            padx=18,
            pady=14
        )

        ctk.CTkLabel(
            info,
            text=f"Batch #{index}",
            font=ctk.CTkFont(
                size=17,
                weight="bold"
            )
        ).pack(
            anchor="w"
        )

        ctk.CTkLabel(
            info,
            text=(
                f"{row['created_at']}   •   "
                f"{row['file_count']} file(s)"
            ),
            text_color="gray60"
        ).pack(
            anchor="w",
            pady=(4, 0)
        )

        if row["undone"]:
            status_text = "● Undone"
            status_color = "gray60"
        else:
            status_text = "● Completed"
            status_color = "#2e8b57"

        ctk.CTkLabel(
            info,
            text=status_text,
            text_color=status_color
        ).pack(
            anchor="w",
            pady=(4, 0)
        )

        if not row["undone"]:
            ctk.CTkButton(
                card,
                text="Undo",
                width=90,
                command=lambda batch_id=row["batch_id"]:
                self.undo_batch(batch_id)
            ).pack(
                side="right",
                padx=18,
                pady=18
            )

    # =============================================================
    # Undo
    # =============================================================

    def undo_batch(self, batch_id: str):
        rows = self.database.get_batch(
            batch_id
        )

        if not rows:
            messagebox.showinfo(
                "Batch not found",
                "This organization batch could not be found."
            )
            return

        if rows[0]["undone"]:
            messagebox.showinfo(
                "Already undone",
                "This batch has already been undone."
            )
            return

        confirm = messagebox.askyesno(
            "Confirm Undo",
            "Are you sure you want to restore the files "
            "from this batch?"
        )

        if not confirm:
            return

        restored = self.undo_manager.undo(
            batch_id
        )

        messagebox.showinfo(
            "Undo complete",
            f"Restored {restored} file(s)."
        )

        self.refresh()
        self.refresh_callback()