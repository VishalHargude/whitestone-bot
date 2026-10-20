"""
scheduler.py - Daily automated execution runner for Emotional & Lovable Cartoon Shorts.
Runs automatically every day at the scheduled time (or immediately via --now).
"""

import argparse
import sys
import time
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import schedule

from config import DAILY_SCHEDULE_TIMES, YOUTUBE_CLIENT_SECRET
from emotional_engine import generate_daily_emotional_short
from uploader import upload_video_to_youtube

def job_daily_emotional_shorts():
    print("\n" + "=" * 60)
    print(f"⏰ [Daily Emotional Cartoon Job Triggered at {time.strftime('%Y-%m-%d %H:%M:%S')}]")
    print("=" * 60)

    try:
        # Step 1: Generate tear-jerking 3D cartoon short
        print("[Scheduler] Generating daily tear-jerking, lovable 3D cartoon Short...")
        result = generate_daily_emotional_short()
        video_path = result["video_path"]

        # Step 2: Auto-upload to YouTube if client_secret exists
        if YOUTUBE_CLIENT_SECRET.exists():
            print("[Scheduler] YouTube credentials found! Starting automatic upload...")
            video_id = upload_video_to_youtube(
                video_path=video_path,
                title=result["title"],
                description=result["description"],
                tags=result["tags"],
                privacy_status="public"
            )
            print(f"[Scheduler] Video is live on YouTube! (Local and Drive storage auto-cleaned)")
        else:
            print("[Scheduler] Note: client_secret.json not found.")
            print(f"[Scheduler] Video is safely saved in output/ directory: {video_path}")
            print("[Scheduler] Add client_secret.json to enable direct auto-uploading and auto-deletion.")

    except Exception as e:
        print(f"[Scheduler] Error during daily run: {e}")

    print("=" * 60 + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Daily Emotional Cartoon Shorts Scheduler")
    parser.add_argument("--now", action="store_true", help="Run the pipeline immediately once")
    args = parser.parse_args()

    if args.now:
        print("[Scheduler] Running immediate single execution...")
        job_daily_emotional_shorts()
    else:
        print("=" * 60)
        print("💖 YouTube Daily Emotional Cartoon Shorts Bot is ACTIVE!")
        print(f"📅 Scheduled to generate 3 videos daily at: {', '.join(DAILY_SCHEDULE_TIMES)}")
        print("   ⏰ 09:00 AM (Morning Peak)")
        print("   ⏰ 02:00 PM (Afternoon Lunch Break)")
        print("   ⏰ 08:00 PM (Prime Time Viral Rush)")
        print("🎭 Content: Clean 3D Pixar Animation (No Subtitles, Pure Emotion)")
        print("💡 Press Ctrl+C anytime to stop.")
        print("=" * 60)

        for sched_time in DAILY_SCHEDULE_TIMES:
            schedule.every().day.at(sched_time).do(job_daily_emotional_shorts)

        while True:
            schedule.run_pending()
            time.sleep(30)
