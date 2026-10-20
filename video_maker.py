"""
video_maker.py - Assembles high-retention Hindi YouTube Shorts with:
1. Real authentic stock video (NASA Space, Ocean, etc.)
2. Fluent native Hindi voiceover
3. Dual-line synchronized subtitles: Spoken Hindi (Yellow) + English Translation (White)
"""

import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
import imageio_ffmpeg

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from config import OUTPUT_DIR, TEMP_DIR, VOICE_NAME
from tts import create_tts_bilingual
from media import prepare_stock_background

def assemble_short(topic_dict: dict, custom_output_name: str = None) -> dict:
    """Complete pipeline to generate a realistic, high-quality YouTube Short."""
    timestamp = int(time.time())
    file_prefix = f"short_{timestamp}"
    title = topic_dict.get("title", "Hindi Short")
    print(f"\n[Video Maker] --- Assembling Short: {title} ---")

    # Step 1: Synthesize bilingual speech & subtitles
    print("[Video Maker] Step 1: Generating natural voiceover and synced bilingual captions...")
    audio_path = TEMP_DIR / "voice.mp3"
    ass_path = TEMP_DIR / "subtitles.ass"

    segments = topic_dict.get("segments", [])
    duration = create_tts_bilingual(segments, audio_path, ass_path, voice=VOICE_NAME)
    padded_duration = duration + 0.4
    print(f"[Video Maker] Audio duration: {duration:.2f} seconds")

    # Step 2: Prepare authentic stock video background
    print("[Video Maker] Step 2: Preparing topic-related HD stock video...")
    stock_filename = topic_dict.get("stock_video", "space_galaxy.mp4")
    bg_video_path = TEMP_DIR / "background.mp4"
    prepare_stock_background(stock_filename, padded_duration, bg_video_path)

    # Step 3: Burn subtitles & merge audio with FFmpeg
    print("[Video Maker] Step 3: Burning bilingual subtitles and final encoding...")
    if custom_output_name:
        final_mp4 = OUTPUT_DIR / f"{custom_output_name}.mp4"
    else:
        final_mp4 = OUTPUT_DIR / f"{file_prefix}.mp4"

    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    # Run inside TEMP_DIR for clean relative path to subtitles.ass
    cmd = [
        ffmpeg_exe, "-y",
        "-i", "background.mp4",
        "-i", "voice.mp3",
        "-vf", "subtitles=subtitles.ass",
        "-c:v", "libx264", "-preset", "fast", "-crf", "19",
        "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        str(final_mp4)
    ]

    res = subprocess.run(cmd, cwd=TEMP_DIR, capture_output=True, text=True)
    if res.returncode != 0:
        print("[Video Maker] FFmpeg Error:", res.stderr[-500:])
        raise RuntimeError("FFmpeg assembly failed")

    # Step 4: Metadata file
    metadata_path = final_mp4.with_suffix(".json")
    meta_info = {
        "title": topic_dict["title"],
        "description": topic_dict["description"],
        "tags": topic_dict["tags"],
        "video_path": str(final_mp4),
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(meta_info, f, ensure_ascii=False, indent=2)

    print(f"[Video Maker] SUCCESS! Video generated at: {final_mp4}")
    print(f"[Video Maker] Size: {os.path.getsize(final_mp4) / (1024*1024):.2f} MB")
    return meta_info
