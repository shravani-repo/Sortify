from __future__ import annotations

import customtkinter as ctk
from tkinter import messagebox


class SettingsFrame(ctk.CTkFrame):
    def __init__(self, master, database, on_rules_changed, **kwargs):
        super().__init__(master, **kwargs)

        self.database = database
        self.on_rules_changed = on_rules_changed

        # Title
        ctk.CTkLabel(
            self,
            text="Settings",
            font=ctk.CTkFont(size=28, weight="bold")
        ).pack(
            anchor="w",
            padx=24,
            pady=(24, 18)
        )

        # Section title
        ctk.CTkLabel(
            self,
            text="Custom extension rules",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(
            anchor="w",
            padx=24,
            pady=(10, 6)
        )

        # Input form
        form = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        form.pack(
            fill="x",
            padx=20
        )

        # Extension input
        self.extension = ctk.CTkEntry(
            form,
            placeholder_text=".csv"
        )
        self.extension.pack(
            side="left",
            padx=4,
            expand=True,
            fill="x"
        )

        # Category input
        self.category = ctk.CTkEntry(
            form,
            placeholder_text="Data Files"
        )
        self.category.pack(
            side="left",
            padx=4,
            expand=True,
            fill="x"
        )

        # Save button
        ctk.CTkButton(
            form,
            text="Save rule",
            command=self.save_rule
        ).pack(
            side="left",
            padx=4
        )

        # Delete button
        ctk.CTkButton(
            form,
            text="Delete rule",
            command=self.delete_rule
        ).pack(
            side="left",
            padx=4
        )

        # Rules display
        self.rules_box = ctk.CTkTextbox(
            self,
            height=220
        )
        self.rules_box.pack(
            fill="both",
            expand=True,
            padx=24,
            pady=20
        )

        self.refresh()

    def save_rule(self):
        extension = self.extension.get().strip()
        category = self.category.get().strip()

        if not extension or not category:
            messagebox.showwarning(
                "Missing information",
                "Enter both an extension and category."
            )
            return

        self.database.save_rule(
            extension,
            category
        )

        self.extension.delete(0, "end")
        self.category.delete(0, "end")

        self.refresh()
        self.on_rules_changed()

        messagebox.showinfo(
            "Rule saved",
            f"Rule saved successfully:\n{extension} → {category}"
        )

    def delete_rule(self):
        extension = self.extension.get().strip()

        if not extension:
            messagebox.showwarning(
                "Missing extension",
                "Enter the extension you want to delete."
            )
            return

        confirm = messagebox.askyesno(
            "Delete rule",
            f"Delete the custom rule for {extension}?"
        )

        if not confirm:
            return

        self.database.delete_rule(extension)

        self.extension.delete(0, "end")
        self.category.delete(0, "end")

        self.refresh()
        self.on_rules_changed()

        messagebox.showinfo(
            "Rule deleted",
            f"Custom rule for {extension} has been deleted."
        )

    def refresh(self):
        self.rules_box.configure(state="normal")
        self.rules_box.delete("1.0", "end")

        rules = self.database.get_rules()

        if not rules:
            self.rules_box.insert(
                "end",
                "No custom rules saved yet.\n"
            )
        else:
            for extension, category in rules.items():
                self.rules_box.insert(
                    "end",
                    f"{extension}  →  {category}\n"
                )

        self.rules_box.configure(state="disabled")