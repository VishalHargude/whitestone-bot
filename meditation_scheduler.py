"""
meditation_scheduler.py - Fully Automated 24/7 Long-Form Meditation Video Scheduler.

Automatically:
1. Generates 30-minute / 1-hour 432Hz deep healing meditation videos.
2. Directly uploads them to YouTube with optimized titles, descriptions, and chapters.
3. Automatically deletes the video file after upload (0 MB disk space used).
4. Runs daily on autopilot at optimal global meditation times.
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

# Optimal global upload times for meditation / sleep music (IST):
# - 06:30 AM IST = Morning meditation in Asia & evening sleep in US/Canada
# - 09:30 PM IST = Night bedtime sleep meditation in Asia & UK afternoon relax
MEDITATION_SCHEDULE_TIMES = ["06:30", "21:30"]

def job_publish_meditation_video(duration_mins: int = 30):
    print("\n" + "=" * 70)
    print(f"🧘‍♂️ [Daily Meditation Auto-Job Triggered at {time.strftime('%Y-%m-%d %H:%M:%S')}]")
    print("=" * 70)

    try:
        # Step 1: Generate Meditation Video
        dur_seconds = duration_mins * 60
        print(f"[Meditation Bot] Step 1: Generating {duration_mins}-Minute 432Hz video...")
        out_video = build_meditation_video(duration_seconds=dur_seconds, output_name=f"meditation_{duration_mins}m_{int(time.time())}")

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

    print("=" * 70 + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automated Meditation YouTube Channel Bot")
    parser.add_argument("--now", action="store_true", help="Generate and upload a 30-minute meditation video immediately")
    parser.add_argument("--duration", type=int, default=30, help="Duration in minutes (e.g. 15, 30, 60)")
    args = parser.parse_args()

    if args.now:
        print(f"[Meditation Bot] Running immediate execution ({args.duration} mins)...")
        job_publish_meditation_video(duration_mins=args.duration)
    else:
        print("=" * 70)
        print("🧘‍♂️ YouTube Meditation Channel Auto-Bot is ACTIVE & RUNNING!")
        print(f"📅 Daily upload schedule: {', '.join(MEDITATION_SCHEDULE_TIMES)}")
        print("   ⏰ 06:30 AM (Global US/EU Bedtime & India Morning Dhyana)")
        print("   ⏰ 09:30 PM (Asia Bedtime & Deep Sleep Relaxation)")
        print("🌿 Mode: 100% Autonomous (Auto-Create -> Auto-Upload -> Auto-Delete)")
        print("💡 Press Ctrl+C anytime to stop.")
        print("=" * 70)

        for sched_time in MEDITATION_SCHEDULE_TIMES:
            schedule.every().day.at(sched_time).do(job_publish_meditation_video, duration_mins=args.duration)

        while True:
            schedule.run_pending()
            time.sleep(30)
