"""
meditation_scheduler.py - Fully Automated 24/7 Long-Form Meditation Video Scheduler.
Supports 1-Hour, 2-Hour, and 3-Hour video durations with 5 alternating thematic worlds.
"""

import argparse
import json
import sys
import time
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import schedule

from config import BASE_DIR
from create_long_meditation_video import build_meditation_video, THEMES
from direct_youtube_upload import upload_latest_video

THEME_TRACKER_FILE = BASE_DIR / "meditation_theme_tracker.json"

# Optimal 3 global peak upload times for meditation & sleep music (IST):
# - 06:00 AM IST = 1-Hour Morning Focus & Awakening (Triggered 05:15 IST)
# - 02:30 PM IST = 1-Hour Midday Stress Relief & Zen Flow (Triggered 13:45 IST)
# - 09:45 PM IST = 2-Hour Deep Sleep Meditation (Triggered 21:00 IST)
MEDITATION_SCHEDULES = [
    {"time": "05:15", "target_public": "06:00 AM IST", "duration_mins": 60, "name": "1-Hour Morning Awakening"},
    {"time": "13:45", "target_public": "02:30 PM IST", "duration_mins": 60, "name": "1-Hour Midday Zen & Stress Relief"},
    {"time": "21:00", "target_public": "09:45 PM IST", "duration_mins": 120, "name": "2-Hour Deep Sleep Meditation"}
]

def get_next_theme_index() -> int:
    """Gets the next theme index and rotates sequentially so themes never repeat."""
    curr_idx = 0
    if THEME_TRACKER_FILE.exists():
        try:
            with open(THEME_TRACKER_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                curr_idx = data.get("last_theme_index", -1) + 1
        except Exception:
            curr_idx = 0
    else:
        curr_idx = int(time.time() // (4 * 3600))

    next_idx = curr_idx % len(THEMES)
    try:
        with open(THEME_TRACKER_FILE, "w", encoding="utf-8") as f:
            json.dump({"last_theme_index": next_idx, "last_updated": time.strftime("%Y-%m-%d %H:%M:%S")}, f)
    except Exception:
        pass

    return next_idx

def job_publish_meditation_video(duration_mins: int = 60, theme_idx: int = None):
    hours = duration_mins / 60.0
    dur_label = f"{int(hours)} Hour" if hours == int(hours) and hours >= 1 else f"{duration_mins} Minutes"
    if hours > 1 and hours == int(hours):
        dur_label = f"{int(hours)} Hours"

    if theme_idx is None:
        theme_idx = get_next_theme_index()

    theme = THEMES[theme_idx % len(THEMES)]

    print("\n" + "=" * 75)
    print(f"🧘‍♂️ [Daily Meditation Auto-Job Triggered at {time.strftime('%Y-%m-%d %H:%M:%S')}]")
    print(f"🎨 Theme: [{theme['name']}] (ID: {theme['id']})")
    print(f"⏱️ Target Duration: {dur_label} ({duration_mins} Minutes)")
    print("=" * 75)

    try:
        # Step 1: Generate Meditation Video with selected theme
        dur_seconds = duration_mins * 60
        print(f"[Meditation Bot] Step 1: Generating {dur_label} Full HD [{theme['name']}] video...")
        out_video = build_meditation_video(
            duration_seconds=dur_seconds,
            theme_index=theme_idx,
            output_name=f"whitestone_{theme['id']}_{duration_mins}m_{int(time.time())}"
        )

        # Step 2: Directly upload to YouTube
        print("\n[Meditation Bot] Step 2: Uploading directly to YouTube channel...")
        url = upload_latest_video()
        if url:
            print(f"🎉 [Meditation Bot] Video successfully published to YouTube: {url}")
            print(f"🧹 Local video automatically deleted. Laptop storage remains 100% free.")
        else:
            print("[!] Upload returned no URL. Please check YouTube authentication.")

    except Exception as e:
        print(f"[!] Error in meditation auto-job: {e}")

    print("=" * 75 + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automated Meditation YouTube Channel Bot")
    parser.add_argument("--now", action="store_true", help="Generate and upload a meditation video immediately")
    parser.add_argument("--duration", type=int, default=60, help="Duration in minutes (e.g. 60 for 1 hr, 120 for 2 hrs, 180 for 3 hrs)")
    parser.add_argument("--theme", type=int, default=None, help="Theme index 0 to 4 (optional)")
    args = parser.parse_args()

    if args.now:
        print(f"[Meditation Bot] Running immediate execution ({args.duration} mins)...")
        job_publish_meditation_video(duration_mins=args.duration, theme_idx=args.theme)
    else:
        print("=" * 75)
        print("🧘‍♂️ YouTube Meditation Channel Auto-Bot is ACTIVE & RUNNING!")
        print("📅 Daily upload schedule (Long-Form Videos):")
        for s in MEDITATION_SCHEDULES:
            print(f"   ⏰ {s['time']} IST -> {s['name']} ({s['duration_mins']} mins)")
        print("🌿 Mode: 100% Autonomous (Auto-Create -> Auto-Upload -> Auto-Delete)")
        print("💡 Press Ctrl+C anytime to stop.")
        print("=" * 75)

        schedule.every().day.at("05:15").do(job_publish_meditation_video, duration_mins=60)
        schedule.every().day.at("13:45").do(job_publish_meditation_video, duration_mins=60)
        schedule.every().day.at("21:00").do(job_publish_meditation_video, duration_mins=120)

        while True:
            schedule.run_pending()
            time.sleep(30)
