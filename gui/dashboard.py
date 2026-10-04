from __future__ import annotations

import customtkinter as ctk


class DashboardFrame(ctk.CTkFrame):
    def __init__(self, master, on_organize, **kwargs):
        super().__init__(master, **kwargs)

        self.on_organize = on_organize

        self.grid_columnconfigure(
            (0, 1, 2, 3),
            weight=1
        )

        self.grid_rowconfigure(
            3,
            weight=1
        )

        # =========================================================
        # Header
        # =========================================================

        ctk.CTkLabel(
            self,
            text="Dashboard",
            font=ctk.CTkFont(
                size=30,
                weight="bold"
            )
        ).grid(
            row=0,
            column=0,
            columnspan=4,
            sticky="w",
            padx=24,
            pady=(24, 4)
        )

        ctk.CTkLabel(
            self,
            text="Overview of your file organization activity",
            text_color="gray60"
        ).grid(
            row=1,
            column=0,
            columnspan=4,
            sticky="w",
            padx=24,
            pady=(0, 20)
        )

        # =========================================================
        # Statistics Cards
        # =========================================================

        self.cards: dict[str, ctk.CTkLabel] = {}

        card_data = (
            ("Files scanned", "Total files detected"),
            ("Images", "Image files"),
            ("Documents", "Document files"),
            ("Media", "Audio and video"),
        )

        for index, (name, description) in enumerate(card_data):

            card = ctk.CTkFrame(
                self,
                corner_radius=16
            )

            card.grid(
                row=2,
                column=index,
                padx=8,
                pady=8,
                sticky="nsew"
            )

            ctk.CTkLabel(
                card,
                text=name,
                font=ctk.CTkFont(
                    size=15,
                    weight="bold"
                )
            ).pack(
                anchor="w",
                padx=18,
                pady=(18, 2)
            )

            ctk.CTkLabel(
                card,
                text=description,
                text_color="gray60"
            ).pack(
                anchor="w",
                padx=18
            )

            value = ctk.CTkLabel(
                card,
                text="0",
                font=ctk.CTkFont(
                    size=28,
                    weight="bold"
                )
            )

            value.pack(
                anchor="w",
                padx=18,
                pady=(12, 18)
            )

            self.cards[name] = value

        # =========================================================
        # Category Breakdown
        # =========================================================

        self.category_card = ctk.CTkFrame(
            self,
            corner_radius=16
        )

        self.category_card.grid(
            row=3,
            column=0,
            columnspan=4,
            sticky="nsew",
            padx=8,
            pady=(18, 8)
        )

        self.category_card.grid_columnconfigure(
            0,
            weight=1
        )

        ctk.CTkLabel(
            self.category_card,
            text="Category Breakdown",
            font=ctk.CTkFont(
                size=19,
                weight="bold"
            )
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=20,
            pady=(18, 2)
        )

        ctk.CTkLabel(
            self.category_card,
            text="Files detected by category",
            text_color="gray60"
        ).grid(
            row=1,
            column=0,
            sticky="w",
            padx=20,
            pady=(0, 14)
        )

        self.category_container = ctk.CTkFrame(
            self.category_card,
            fg_color="transparent"
        )

        self.category_container.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=20,
            pady=(0, 18)
        )

        # Initial state
        self.show_empty_categories()

        # =========================================================
        # Ready to Organize
        # =========================================================

        info_card = ctk.CTkFrame(
            self,
            corner_radius=16
        )

        info_card.grid(
            row=4,
            column=0,
            columnspan=4,
            sticky="ew",
            padx=8,
            pady=(10, 10)
        )

        ctk.CTkLabel(
            info_card,
            text="Ready to organize?",
            font=ctk.CTkFont(
                size=20,
                weight="bold"
            )
        ).pack(
            anchor="w",
            padx=20,
            pady=(18, 4)
        )

        ctk.CTkLabel(
            info_card,
            text=(
                "Select a folder and let Smart File Organizer "
                "automatically sort your files."
            ),
            text_color="gray60"
        ).pack(
            anchor="w",
            padx=20
        )

        ctk.CTkButton(
            info_card,
            text="Organize Files",
            command=on_organize,
            height=40
        ).pack(
            anchor="w",
            padx=20,
            pady=18
        )

        # =========================================================
        # Tip
        # =========================================================

        ctk.CTkLabel(
            self,
            text=(
                "Tip: Use Preview before organizing to see exactly "
                "where your files will be moved."
            ),
            text_color="gray60"
        ).grid(
            row=5,
            column=0,
            columnspan=4,
            sticky="w",
            padx=24,
            pady=16
        )

    # =============================================================
    # Update Statistics
    # =============================================================

    def update_stats(
        self,
        stats: dict[str, int]
    ) -> None:

        mapping = {
            "Files scanned": "total",
            "Images": "Images",
            "Documents": "Documents",
            "Media": "media"
        }

        for label, key in mapping.items():
            self.cards[label].configure(
                text=str(
                    stats.get(
                        key,
                        0
                    )
                )
            )

        self.update_categories(
            stats.get(
                "categories",
                {}
            )
        )

    # =============================================================
    # Category Breakdown
    # =============================================================

    def update_categories(
        self,
        categories: dict[str, int]
    ) -> None:

        for widget in self.category_container.winfo_children():
            widget.destroy()

        if not categories:
            self.show_empty_categories()
            return

        max_count = max(
            categories.values()
        )

        for index, (category, count) in enumerate(
            sorted(
                categories.items(),
                key=lambda item: item[1],
                reverse=True
            )
        ):

            row = ctk.CTkFrame(
                self.category_container,
                fg_color="transparent"
            )

            row.grid(
                row=index,
                column=0,
                sticky="ew",
                pady=4
            )

            row.grid_columnconfigure(
                1,
                weight=1
            )

            ctk.CTkLabel(
                row,
                text=category,
                width=100,
                anchor="w",
                font=ctk.CTkFont(
                    size=13,
                    weight="bold"
                )
            ).grid(
                row=0,
                column=0,
                padx=(0, 10)
            )

            progress = ctk.CTkProgressBar(
                row,
                height=10
            )

            progress.grid(
                row=0,
                column=1,
                sticky="ew",
                padx=5
            )

            if max_count > 0:
                progress.set(
                    count / max_count
                )
            else:
                progress.set(0)

            ctk.CTkLabel(
                row,
                text=str(count),
                width=40,
                anchor="e",
                font=ctk.CTkFont(
                    size=13,
                    weight="bold"
                )
            ).grid(
                row=0,
                column=2,
                padx=(10, 0)
            )

    # =============================================================
    # Empty Category State
    # =============================================================

    def show_empty_categories(self):
        for widget in self.category_container.winfo_children():
            widget.destroy()

        ctk.CTkLabel(
            self.category_container,
            text="No files detected yet.",
            text_color="gray60"
        ).pack(
            anchor="w",
            pady=8
        )