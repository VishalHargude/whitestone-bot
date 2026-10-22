"""
generate_gentle_rain.py - Generates seamless loopable 10-second 1920x1080
subtle, relaxing, gentle falling rain streak overlay video.
"""

import math
import random
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw

BASE_DIR = Path(r"C:\Users\Vishal Hargude\.gemini\antigravity\scratch\hindi_shorts_generator")
ASSETS_DIR = BASE_DIR / "assets"
OUT_RAIN_MP4 = ASSETS_DIR / "rain_falling_gentle.mp4"
ffmpeg_exe = r'C:\Users\Vishal Hargude\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe'

WIDTH, HEIGHT = 1920, 1080
FPS = 30
DURATION_SEC = 10
TOTAL_FRAMES = FPS * DURATION_SEC

random.seed(108)

# 240 gentle slanted rain streaks
NUM_DROPS = 240
drops = []
for _ in range(NUM_DROPS):
    # Streak length: 18 to 45 px, width 1 to 2 px, slanted angle ~15 degrees
    length = random.uniform(22, 48)
    alpha = random.randint(55, 120)
    thickness = 1 if random.random() < 0.75 else 2
    # Speed: wraps vertically 3 to 5 times in 10 seconds (fast natural raindrops)
    wraps_y = random.choice([3, 4, 5])
    # Slight horizontal drift matching 15 degree angle: dx = dy * tan(15 deg) ~= dy * 0.26
    wraps_x = wraps_y * 0.26

    init_x = random.uniform(0, WIDTH)
    init_y = random.uniform(0, HEIGHT)

    drops.append({
        "init_x": init_x,
        "init_y": init_y,
        "length": length,
        "alpha": alpha,
        "thickness": thickness,
        "wraps_y": wraps_y,
        "wraps_x": wraps_x
    })

print(f"[Rain Generator] Rendering {TOTAL_FRAMES} frames of relaxing rain overlay...")

cmd = [
    ffmpeg_exe, "-y",
    "-f", "rawvideo",
    "-vcodec", "rawvideo",
    "-s", f"{WIDTH}x{HEIGHT}",
    "-pix_fmt", "rgba",
    "-r", str(FPS),
    "-i", "-",
    "-c:v", "libx264",
    "-preset", "veryfast",
    "-crf", "18",
    "-pix_fmt", "yuv420p",
    str(OUT_RAIN_MP4)
]

proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)

angle_rad = math.radians(16)
cos_a = math.cos(angle_rad)
sin_a = math.sin(angle_rad)

for f_idx in range(TOTAL_FRAMES):
    progress = f_idx / TOTAL_FRAMES
    frame = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(frame)

    for d in drops:
        # Wrap positions seamlessly
        y1 = (d["init_y"] + d["wraps_y"] * HEIGHT * progress) % HEIGHT
        x1 = (d["init_x"] - d["wraps_x"] * WIDTH * progress) % WIDTH

        # Streak tail
        x2 = x1 - d["length"] * sin_a
        y2 = y1 - d["length"] * cos_a

        c = (220, 235, 255, d["alpha"])
        draw.line([(x1, y1), (x2, y2)], fill=c, width=d["thickness"])

    proc.stdin.write(frame.tobytes())

proc.stdin.close()
proc.wait()
print(f"[OK] Generated seamless gentle rain overlay: {OUT_RAIN_MP4} ({OUT_RAIN_MP4.stat().st_size / (1024*1024):.2f} MB)")
