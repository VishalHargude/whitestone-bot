"""
meditation_scheduler.py - Fully Automated 24/7 Long-Form Meditation Video Scheduler.
Supports 1-Hour, 2-Hour, and 3-Hour video durations with automatic upload and cleanup.
"""

import argparse
import sys
import time
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import schedule

from config import BASE_DIR
from create_long_meditation_video import build_meditation_video
from direct_youtube_upload import upload_latest_video

# Optimal 3 global upload times for meditation / sleep music (IST):
# - 06:30 AM IST = 1-Hour Morning Dhyana (Asia Morning & US Evening)
# - 02:30 PM IST = 1-Hour Afternoon Stress Relief & Zen Focus
# - 09:30 PM IST = 2-Hour Deep Sleep Relaxation (Asia Bedtime & Deep Insomnia Relief)
MEDITATION_SCHEDULES = [
    {"time": "06:30", "duration_mins": 60, "name": "1-Hour Morning Dhyana"},
    {"time": "14:30", "duration_mins": 60, "name": "1-Hour Afternoon Zen"},
    {"time": "21:30", "duration_mins": 120, "name": "2-Hour Deep Sleep Meditation"}
]

def job_publish_meditation_video(duration_mins: int = 60):
    hours = duration_mins / 60.0
    dur_label = f"{int(hours)} Hour" if hours == int(hours) and hours >= 1 else f"{duration_mins} Minutes"
    if hours > 1 and hours == int(hours):
        dur_label = f"{int(hours)} Hours"

    print("\n" + "=" * 75)
    print(f"🧘‍♂️ [Daily Meditation Auto-Job Triggered at {time.strftime('%Y-%m-%d %H:%M:%S')}]")
    print(f"⏱️ Target Duration: {dur_label} ({duration_mins} Minutes)")
    print("=" * 75)

    try:
        # Step 1: Generate Meditation Video
        dur_seconds = duration_mins * 60
        print(f"[Meditation Bot] Step 1: Generating {dur_label} Full HD 432Hz video...")
        out_video = build_meditation_video(duration_seconds=dur_seconds, output_name=f"whitestone_{duration_mins}m_{int(time.time())}")

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
    args = parser.parse_args()

    if args.now:
        print(f"[Meditation Bot] Running immediate execution ({args.duration} mins)...")
        job_publish_meditation_video(duration_mins=args.duration)
    else:
        print("=" * 75)
        print("🧘‍♂️ YouTube Meditation Channel Auto-Bot is ACTIVE & RUNNING!")
        print("📅 Daily upload schedule (Long-Form Videos):")
        for s in MEDITATION_SCHEDULES:
            print(f"   ⏰ {s['time']} IST -> {s['name']} ({s['duration_mins']} mins)")
        print("🌿 Mode: 100% Autonomous (Auto-Create -> Auto-Upload -> Auto-Delete)")
        print("💡 Press Ctrl+C anytime to stop.")
        print("=" * 75)

        schedule.every().day.at("06:30").do(job_publish_meditation_video, duration_mins=60)
        schedule.every().day.at("14:30").do(job_publish_meditation_video, duration_mins=60)
        schedule.every().day.at("21:30").do(job_publish_meditation_video, duration_mins=120)

        while True:
            schedule.run_pending()
            time.sleep(30)
