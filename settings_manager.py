# settings_manager.py

import os
import json

DEFAULT_SETTINGS = {
    "is_dark_mode": False,
    "font_family": "Arial",  # default to a sans font
    "font_size": 10,
    "font_bold": False,
    "default_tags": ["breakfast", "lunch", "dinner", "dessert", "appetizer", "cocktail"]
}

SETTINGS_FILE = "settings.json"

def load_settings():
    """
    Load settings from a local JSON file.
    If the file doesn't exist, return DEFAULT_SETTINGS.
    """
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Merge with defaults to ensure all keys exist
            merged = DEFAULT_SETTINGS.copy()
            merged.update(data)
            return merged
        except Exception as e:
            print(f"Error loading settings file: {e}")
            return DEFAULT_SETTINGS.copy()
    else:
        return DEFAULT_SETTINGS.copy()

def save_settings(settings: dict):
    """
    Save current settings to a JSON file.
    """
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
    except Exception as e:
        print(f"Error saving settings: {e}")
