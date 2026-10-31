"""
VRChat AI Translator Pro
Entry Point Script
"""

import sys
import os
import customtkinter as ctk

# Ensure src directory is in path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.config import ConfigManager
from src.ui.app_window import AppWindow


def main():
    # Configure CustomTkinter defaults
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")

    # Load configuration
    config_path = os.path.join(PROJECT_ROOT, "config.json")
    config = ConfigManager(config_path=config_path)

    # Launch application
    app = AppWindow(config=config)
    app.mainloop()


if __name__ == "__main__":
    main()
