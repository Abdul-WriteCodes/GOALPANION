# utils/progress_manager.py

import json
import os

PROGRESS_FILE = "data/progress.json"

def load_progress(goal_id):
    """Load progress for a specific goal"""
    if not os.path.exists(PROGRESS_FILE):
        return {}
    with open(PROGRESS_FILE, "r") as f:
        data = json.load(f)
    return data.get(goal_id, {})

def save_progress(goal_id, progress_dict):
    """Save progress for a specific goal"""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            data = json.load(f)
    else:
        data = {}
    data[goal_id] = progress_dict
    with open(PROGRESS_FILE, "w") as f:
        json.dump(data, f, indent=4)
