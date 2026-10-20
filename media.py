"""
media.py - Provides authentic, HD vertical stock videos for each topic.
Uses pre-installed authentic NASA space videos and ocean wildlife footage in assets/stock_videos/.
"""

import subprocess
from pathlib import Path
import imageio_ffmpeg

from config import ASSETS_DIR, TEMP_DIR, VIDEO_WIDTH, VIDEO_HEIGHT, FPS

STOCK_DIR = ASSETS_DIR / "stock_videos"
STOCK_DIR.mkdir(parents=True, exist_ok=True)

def prepare_stock_background(video_filename: str, target_duration: float, output_path: Path) -> Path:
    """
    Loops or trims the requested real stock video to match the audio duration.
    Forces clean 1080x1920 (9:16 vertical) format.
    """
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    stock_source = STOCK_DIR / video_filename

    # If the specific stock video isn't there, fallback to space_galaxy.mp4
    if not stock_source.exists():
        fallback = STOCK_DIR / "space_galaxy.mp4"
        if fallback.exists():
            stock_source = fallback
        else:
            raise FileNotFoundError(f"Stock video not found: {stock_source}")

    print(f"[Media] Using authentic stock video: {stock_source.name} (Duration: {target_duration:.2f}s)")

    cmd = [
        ffmpeg_exe, "-y",
        "-stream_loop", "-1",
        "-i", str(stock_source),
        "-t", str(target_duration),
        "-vf", f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:force_original_aspect_ratio=increase,crop={VIDEO_WIDTH}:{VIDEO_HEIGHT}",
        "-r", str(FPS),
        "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p",
        "-an",
        str(output_path)
    ]
    subprocess.run(cmd, capture_output=True, check=True)
    return output_path
