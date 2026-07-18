"""
Utility functions for the CP Dashboard Contest Fetcher.
"""

import json
import os
from datetime import datetime

def get_local_timezone():
    """
    Returns the local timezone based on the system's current setting.
    """
    return datetime.now().astimezone().tzinfo

def format_unix_time(unix_seconds):
    """
    Converts a Unix timestamp (in seconds) to an ISO-8601 string with local timezone.
    """
    local_tz = get_local_timezone()
    dt = datetime.fromtimestamp(unix_seconds, tz=local_tz)
    return dt.isoformat()

def load_json(filepath):
    """
    Safely load a JSON file.
    """
    if not os.path.exists(filepath):
        return None
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None

def save_json(data, filepath):
    """
    Safely save data to a JSON file.
    """
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving to {filepath}: {e}")
        return False
