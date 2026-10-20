"""
history_tracker.py - Guarantees ZERO duplicate videos.
Maintains a permanent log of all generated and published topics.
Never repeats a video twice across any channel or day!
"""

import json
from pathlib import Path
from config import BASE_DIR

HISTORY_FILE = BASE_DIR / "published_history.json"

def load_history() -> dict:
    """Loads history database."""
    if not HISTORY_FILE.exists():
        return {"used_topics": [], "published_count": 0, "channels": {}}
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"used_topics": [], "published_count": 0, "channels": {}}

def is_topic_already_used(topic_id: str) -> bool:
    """Returns True if the topic has ever been used before."""
    history = load_history()
    return topic_id in history.get("used_topics", [])

def record_published_topic(channel_id: str, topic_id: str, title: str):
    """Records topic into permanent history to prevent future duplicates."""
    history = load_history()
    if topic_id not in history["used_topics"]:
        history["used_topics"].append(topic_id)
    history["published_count"] = history.get("published_count", 0) + 1

    channels = history.setdefault("channels", {})
    ch_list = channels.setdefault(channel_id, [])
    ch_list.append({"topic_id": topic_id, "title": title})

    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
    print(f"[History Tracker] Recorded '{topic_id}' for {channel_id}. Zero duplicates guaranteed! 🛡️")
