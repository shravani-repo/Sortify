from __future__ import annotations

import customtkinter as ctk


# Application appearance
APPEARANCE_MODE = "System"

# Main application color theme
COLOR_THEME = "blue"


def setup_theme() -> None:
    """Configure the global appearance of the application."""

    ctk.set_appearance_mode(APPEARANCE_MODE)
    ctk.set_default_color_theme(COLOR_THEME)